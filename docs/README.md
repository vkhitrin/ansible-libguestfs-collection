# Documentation

## Modules

Full documentation(ansible-doc) is present inside the module.

| Module                   | Description                | Documentation                                   |
|:------------------------:|:--------------------------:|:-----------------------------------------------:|
| guestfs_command          | Execute commands           | [doc](/plugins/modules/guestfs_command.py)      |
| guestfs_package          | Manage packages            | [doc](/plugins/modules/guestfs_package.py)      |
| guestfs_user             | Manage users               | [doc](/plugins/modules/guestfs_user.py)         |
| guestfs_copy_out         | Fetch files                | [doc](/plugins/modules/guestfs_download.py)     |
| guestfs_copy_in          | Upload files               | [doc](/plugins/modules/guestfs_upload.py)       |

## Sample Play

Assumes you have everything installed (mentioned in [repo's README Prerequisites](/README.md#Prerequisites)).

### Install package on image located on localhost:

Download a CentOS cloud image to /tmp:

`curl https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1809.qcow2 -o /tmp/CentOS-7-x86_64-GenericCloud-1809.qcow2`

Run playbook on localhost:

`ansible-playbook docs/samples/main.yml -i hosts`
