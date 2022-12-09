#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Vadim Khitrin <me at vkhitrin.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import re
try:
    import guestfs
    HAS_GUESTFS = True
except ImportError:
    HAS_GUESTFS = False

from collections import OrderedDict


class guest():
    def __init__(self, module):
        self.mount = False
        self.automount = False
        self.mounts = False
        self.module = module
        self.handle = None
        self.network = False
        self.image = None
        self.se_relabel = False
        if HAS_GUESTFS is False:
            results = {}
            results['msg'] = "libguestfs Python bindings are required for this module"
            self.module.fail_json(**results)

    def mount_device(self, device, mountpoint):
        return self.handle.mount(device, mountpoint)

    def bootstrap(self):
        results = {}
        ansible_module_params = self.module.params
        self.image = ansible_module_params.get('image')
        self.automount = ansible_module_params.get('automount')
        self.mounts = ansible_module_params.get('mounts')
        self.network = ansible_module_params.get('network')
        if self.mounts and self.automount:
            results['msg'] = 'Automount (enabled by default) and manual mounts were requested by module, please disable automount if providing manual mounts'
            self.module.fail_json(**results)
        if os.path.exists(self.image) is False:
            results['msg'] = 'Could not find image'
            self.module.fail_json(**results)
        self.handle = guestfs.GuestFS(python_return_dict=True)
        self.handle.add_drive_opts(self.image, readonly=0)
        if self.network:
            self.handle.set_network(True)
        try:
            self.handle.launch()
        except Exception as e:
            results['msg'] = 'Could not mount guest disk image, python exception: {}'.format(str(e))
            self.module.fail_json(**results)
        roots = self.handle.inspect_os()
        if self.automount:
            if len(roots) == 0:
                results['msg'] = 'Automount failed, no devices were found in guest disk image, consider attempting manual mount'
                self.module.fail_json(**results)
            for root in roots:
                mps = self.handle.inspect_get_mountpoints(root)
                # Filter the mountpoint mapped to root device, do not attempt to mount partitions
                filtered_mounts = list(filter(lambda m: mps[m] == root, mps))
                if not filtered_mounts:
                    results['msg'] = 'Failed to detect associated mountpoint for device {}.'.format(str(root))
                    self.module.fail_json(**results)
                try:
                    self.mount_device(root, filtered_mounts[0])
                except RuntimeError as e:
                    results['msg'] = "Couldn't mount device inside guest disk image, python exception: {}".format(str(e))
                    self.module.fail_json(**results)
        else:
            if not self.mounts:
                results['msg'] = "Automount is disabled and no mountpoints were provided to module"
                self.module.fail_json(**results)
            for mount_request in self.mounts:
                if len(mount_request.keys()) > 1:
                    results['msg'] = "Dictionary '{}' is expected to have a single key".format(mount_request)
                    self.module.fail_json(**results)
                device, mountpoint = mount_request.popitem()
                try:
                    self.mount_device(device, mountpoint)
                except RuntimeError as e:
                    results['msg'] = "Couldn't mount device inside guest disk image, python exception: {}".format(str(e))
                    self.module.fail_json(**results)
        self.mount = True
        return self.handle

    def close(self):
        self.image = self.module.params.get('image')
        if self.handle:
            if self.mount:
                # Relabel SELinux contexts
                if self.se_relabel:
                    selinux_config = self.handle.read_lines("/etc/selinux/config")
                    re_policy = re.compile("SELINUXTYPE=(?P<policy>.*)")
                    if re_policy:
                        self.handle.rm_f("/.autorelabel")
                        selinux_policy_line = list(filter(re_policy.match, selinux_config))
                        if selinux_policy_line:
                            selinux_policy_string = re.search(re_policy, selinux_policy_line[0])
                            selinux_policy = selinux_policy_string.group('policy')
                            selinux_spec_file = "/etc/selinux/{}/contexts/files/file_contexts".format(selinux_policy)
                            if self.handle.exists(selinux_spec_file) == 1:
                                self.handle.selinux_relabel(selinux_spec_file, "/", force=True)
                    else:
                        self.handle.touch("/.autorelabel")
                self.handle.umount_all()
            # Backwards compatibility, autosync is enabled by default since libguestfs 1.5.24
            self.handle.sync()
            # Shut off appliance before closing handle
            self.handle.shutdown()
            self.handle.close()
            return True
        return False
