#!/usr/vin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Vadim Khitrin <me at vkhitrin.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: guestfs_command
short_description: Execute commands on guest image
version_added: '2.8'
description:
  - Execute commands on guest images
options:
  image:
    required: True
    description: Image path on filesystem
  shell:
    required: False
    description: List of commands to run in shell (commands are invoked from /usr/bin/sh), shell and command are mutually exclusive
  command:
    required: False
    description: List of commands to run directly from binaries, shell and command are mutually exclusive
  automount:
    required: False
    description: Whether to perform auto mount of mountpoints inside guest disk image (REQUIRED for this module)
    default: True
  network:
    required: False
    description: Whether to enable network for appliance
    default: True
  selinux_relabel:
    required: False
    description: Whether to perform SELinux context relabeling
    default: False
notes:
  - stderr output is not available in libguestfs
requirements:
  - "libguestfs"
  - "libguestfs-devel"
  - "python >= 2.7.5 || python >= 3.4"
author:
  - Vadim Khitrin (@vkhitrin)
"""

EXAMPLES = """
- name: Executes a shell command
  guestfs_command:
    image: /tmp/rhel7-5.qcow2
    shell: 'ls -l'

- name: Executes binaries with no access to network
  guestfs_command:
    image: /tmp/rhel7-5.qcow2
    command: 'systemctl reboot'
    network: False
"""

RETURN = """
msg:
  type: string
  when: failure
  description: contains the error message (may include python exceptions)
  example: "cat: /fgdfgdfg/dfgdfg: No such file or directory"

stdout:
  type: string
  when: success
  description: when commands is executed succesffuly and returns stdout string
  example: "hello world"

stdout_lines:
  type: list
  when: success
  description: when commands is executed succesffuly and returns stdoud formatted by new lines
  example: [
      "hello",
      "world"
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.libguestfs import guest

import re


def execute(guest, module):

    results = {
        'changed': False,
        'failed': False,
    }
    err = False

    # Create a command variable
    if module.params['shell']:
        cmd = module.params['shell']
    elif module.params['command']:
        cmd = module.params['command']

    try:
        if module.params['shell']:
            result = guest.sh(cmd)
        elif module.params['command']:
            # Split sentence into words using regular expressions
            cmd_args = re.findall(r'([^\s]+)', cmd)
            result = guest.command(cmd_args)
    except Exception as e:
        err = True
        results['failed'] = True
        error_message = str(e)
        if error_message in ['command: ', 'sh: ']:
            error_message = 'command has returned stderr to shell but guestfs does not return it'
        results['msg'] = error_message

    if not err:
        results['changed'] = True
        results['stdout'] = result.rstrip('\n')
        results['stdout_lines'] = results['stdout'].split('\n')

    return results, err


def main():

    mutual_exclusive_args = [['command', 'shell']]
    required_one_of_args = [['command', 'shell']]
    module = AnsibleModule(
        argument_spec=dict(
            image=dict(required=True, type='str'),
            automount=dict(required=False, type='bool', default=True),
            network=dict(required=False, type='bool', default=True),
            selinux_relabel=dict(required=False, type='bool', default=False),
            command=dict(required=False, type='str'),
            shell=dict(required=False, type='str'),
            debug=dict(required=False, type='bool', default=False),
        ),
        mutually_exclusive=mutual_exclusive_args,
        required_one_of=required_one_of_args,
        supports_check_mode=False
    )

    g = guest(module)
    instance = g.bootstrap()
    results, err = execute(instance, module)
    g.close()

    if err:
        module.fail_json(**results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
