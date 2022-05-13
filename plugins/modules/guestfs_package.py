#!/usr/vin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Vadim Khitrin <me at vkhitrin.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: guestfs_package
short_description: Manage packages on guest image
version_added: '2.8'
description:
  - Manage packages on guest image
options:
  image:
    required: True
    description: Image path on filesystem
  name:
    required: False
    description: List of packages to manipulate, name and list are mutually exclusive
  state:
    required: True
    description: action to be performed
    choices:
    - present
    - absent
  list:
    required: False
    description: String to match when querying installed packages, to display all insert '*', name and list are mutually exclusive
  automount:
    required: False
    description: Whether to perform auto mount of mountpoints inside guest disk image
    default: True
  mounts:
    required: False
    description: "List of mounts that will be attempted. Each element is a dictionary {'/path/to/device': '/path/to/mountpoint'}"
  network:
    required: False
    description: Whether to enable network for appliance
    default: True
  selinux_relabel:
    required: False
    description: Whether to perform SELinux context relabeling
    default: False
notes:
  - Currently only guest images with dnf,yum and apt package managers are supported
requirements:
  - "libguestfs"
  - "libguestfs-devel"
  - "python >= 2.7.5 || python >= 3.4"
author:
  - Vadim Khitrin (@vkhitrin)
"""

EXAMPLES = """
- name: Installs a single package
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    name: vim
    state: present

- name: Installs several packages
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    name:
      - vim
      - nc
      - telnet
    state: present

- name: Uninstalls a single package
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    name: vim
    state: absent

- name: Uninstalls several package
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    name:
      - vim
      - nc
      - telnet
    state: absent

- name: List all packages containing string 'yum'
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    list: yum

- name: List all packages
  guestfs_package:
    image: /tmp/rhel7-5.qcow2
    list: '*'
"""

RETURN = """
msg:
  type: string
  when: failure
  description: Contains the error message (may include python exceptions)
  example: "Unable to locate package testpackage123"

results:
  type: array
  when: success
  description: Contains the module successful execution results
  example: [
      "2:vim-enhanced-7.4.160-4.el7.x86_64 is present"
  ]

log:
  type: array
  when: available and invoked
  description: displays debug info
  example: [
      "Loaded plugins: search-disabled-repos",
      "No Packages marked for removal"
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.libguestfs import guest

import re

PACKAGE_MANAGERS = {
    'dnf': {'present': 'dnf -y install', 'absent': 'dnf -y remove'},
    'yum': {'present': 'yum -y install', 'absent': 'yum -y remove'},
    'apt': {'present': 'apt-get -y install', 'absent': 'apt-get -y remove'}
}


def packages(guest, module):

    state = module.params['state']
    results = {
        'changed': False,
        'failed': False
    }
    # Use set to be converted into list since yum/dnf querying could contain same value multiple times
    response = set()
    err = False

    if module.params['name']:
        packages_string = ' '.join(module.params['name'])
        for mount in guest.mounts():
            package_manager = guest.inspect_get_package_management(mount)
            # If libguest managed to find package manager, quit loop
            if package_manager != 'unknown' and package_manager:
                break

        if package_manager in PACKAGE_MANAGERS:
            try:
                result = guest.sh_lines('{command} {packages}'.format(command=PACKAGE_MANAGERS[package_manager][state],
                                                                      packages=packages_string))
            except Exception as e:
                err = True
                results['failed'] = True
                results['msg'] = str(e)

            if package_manager in ['yum', 'dnf'] and not err:
                results['log'] = '\n'.join(result)
                for line in result:
                    for package in module.params['name']:
                        if package in line:
                            if 'Verifying' in line:
                                results['changed'] = True
                                # Split sentence into words using regular expressions
                                invoked_package = re.findall(r'([^\s]+)', line)[2]
                                response.add('{package} is {state}'.format(package=invoked_package, state=state))
                            elif 'already installed' in line:
                                response.add(line.replace('Package ', ''))
                            elif 'No package {package} available.'.format(package=package) in line:
                                results['failed'] = True
                                results['msg'] = line

                        if 'No Packages marked for removal' in line:
                            response.add(line)

            elif package_manager == 'apt' and not err:
                for line in result:
                    for package in module.params['name']:
                        if package in line:
                            if "Unpacking" in line or "Removing" in line:
                                results['changed'] = True
                                # Substitute string using regular expression and remove CR
                                invoked_package = re.sub(r'Unpacking|Removing', '', line).replace(' ...\r', '')
                                response.add('{package} is {state}'.format(package=invoked_package, state=state))
                            elif "aready" in line or "not installed" in line:
                                response.add(line)

            if not err:
                results['results'] = list(sorted(response))

        else:
            err = True
            results['msg'] = 'Package manager {package_manager} is not supported'.format(package_manager=package_manager)

    elif module.params['list']:
        app_regex = module.params['list']
        if app_regex != "*":
            app_query = True
        else:
            app_query = False
        packages_list = []
        for mount in guest.mounts():
            apps = guest.inspect_list_applications2(mount)
            if apps:
                for app in apps:
                    packages_list.append('{name}-{version}-{release}-{arch}'.format(name=app['app2_name'],
                                                                                    version=app['app2_version'],
                                                                                    release=app['app2_release'],
                                                                                    arch=app['app2_arch']))
                    if app_query:
                        if not re.match(app_regex, app['app2_name']):
                            del packages_list[-1]
                break

        if packages_list:
            results['results'] = packages_list
        else:
            err = True
            results['msg'] = "Packages containing regular expression '{regexp}' not found".format(regexp=app_regex)

    return results, err


def main():

    mutual_exclusive_args = [
        ['name', 'list'],
        ['list', 'state']
    ]
    required_togheter_args = [['name', 'state']]
    required_one_of_args = [['name', 'list']]

    module = AnsibleModule(
        argument_spec=dict(
            image=dict(required=True, type='str'),
            automount=dict(required=False, type='bool', default=True),
            mounts=dict(required=False,  type='list', elements='dict'),
            network=dict(required=False, type='bool', default=True),
            selinux_relabel=dict(required=False, type='bool', default=False),
            name=dict(required=False, type='list'),
            state=dict(required=False, choices=['present', 'absent']),
            list=dict(required=False, type='str'),
        ),
        mutually_exclusive=mutual_exclusive_args,
        required_one_of=required_one_of_args,
        required_together=required_togheter_args,
        supports_check_mode=False
    )

    g = guest(module)
    instance = g.bootstrap()
    results, err = packages(instance, module)
    g.close()

    if err:
        module.fail_json(**results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
