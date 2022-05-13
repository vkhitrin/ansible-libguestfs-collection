#!/usr/vin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Vadim Khitrin <me at vkhitrin.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: guestfs_user
short_description: Manages users in guest image
version_added: '2.8'
description:
  - Manages users in guest image
options:
  image:
    required: True
    description: Image path on filesystem
  name:
    required: True
    description: Name of user to manage
  password:
    required: False
    description: User's password
  state:
    required: True
    description: Action to be performed
    choices:
    - present
    - absent
  automount:
    required: False
    description: Whether to perform auto mount of mountpoints inside guest disk image (REQUIRED for this module)
    default: True
  mounts:
    required: False
    description: List of mounts that will be attempted. Each element is a dictionary {'/path/to/device': '/path/to/mountpoint'}
  selinux_relabel:
    required: False
    description: Whether to perform SELinux context relabeling
  network:
    required: False
    description: Whether to enable network for appliance
    default: True
requirements:
  - "libguestfs"
  - "libguestfs-devel"
  - "python >= 2.7.5 || python >= 3.4"
author:
  - Vadim Khitrin (@vkhitrin)
"""

EXAMPLES = """
- name: Creates a user
  guestfs_user:
    image: /tmp/rhel7-5.qcow2
    user: test_user
    password: test_password
    state: present

- name: Change password to an existing user
  guestfs_user:
    image: /tmp/rhel7-5.qcow2
    user: root
    password: root_password
    state: present

- name: Delete a user
  guestfs_user:
    image: /tmp/rhel7-5.qcow2
    user: root
    password: root_password
    state: absent
"""

RETURN = """
msg:
  type: string
  when: failure
  description: Contains the error message (may include python exceptions)
  example: "cat: /fgdfgdfg/dfgdfg: No such file or directory"

results:
  type: array
  when: success
  description: Contains the module successful execution results
  example: [
      "test_user is present"
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.libguestfs import guest


def users(guest, module):

    state = module.params['state']
    user_name = module.params['name']
    user_password = module.params['password']
    results = {
        'changed': False,
        'failed': False,
        'results': []
    }
    err = False

    try:
        guest.sh_lines('id -u {}'.format(user_name))
        user_exists = True
    except Exception:
        user_exists = False

    if state == 'present':
        if user_exists:
            try:
                guest.sh_lines('echo {u}:{p} | chpasswd'.format(u=user_name,
                                                                p=user_password))
            except Exception as e:
                err = True
                results['failed'] = True
                results['msg'] = str(e)

        else:
            try:
                guest.sh_lines('useradd {user}'.format(user=user_name))
                guest.sh_lines('{u}:{p} | chpasswd'.format(u=user_name,
                                                           p=user_password))
            except Exception as e:
                err = True
                results['failed'] = True
                results['msg'] = str(e)

    elif state == 'absent':
        if user_exists:
            try:
                guest.sh_lines('userdel {user}'.format(user=user_name))
            except Exception as e:
                err = True
                results['failed'] = True
                results['msg'] = str(e)

    if not err:
        results['changed'] = True
        results['results'].append('{u} is {s}'.format(u=user_name, s=state))

    return results, err


def main():

    required_togheter_args = [['name', 'state']]
    module = AnsibleModule(
        argument_spec=dict(
            image=dict(required=True, type='str'),
            automount=dict(required=False, type='bool', default=True),
            mounts=dict(required=False,  type='list', elements='dict'),
            network=dict(required=False, type='bool', default=True),
            selinux_relabel=dict(required=False, type='bool', default=False),
            name=dict(required=True, type='str'),
            password=dict(type='str', no_log=True),
            state=dict(required=True, choices=['present', 'absent']),
            debug=dict(required=False, type='bool', default=False),
            force=dict(required=False, type='bool', default=False)
        ),
        required_together=required_togheter_args,
        supports_check_mode=False
    )

    if not module.params['password'] and module.params['state'] == 'present':
        err = True
        results = {
            'msg': 'Please provide password when using present state'
        }
        module.fail_json(**results)

    g = guest(module)
    instance = g.bootstrap()
    results, err = users(instance, module)
    g.close()

    if err:
        module.fail_json(**results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
