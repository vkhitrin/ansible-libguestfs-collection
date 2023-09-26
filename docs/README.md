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

## Sample Plays

Make sure everything is installed (mentioned in [README Prerequisites](/README.md#Prerequisites)) on the Ansible controller host.  
All plays by default will run on `localhost` unless overridden by `hosts_pattern` variable.  

### Execute command

[install_packages.yml](/docs/samples/install_packages.yml)

Downloads CentOS image and executes `df -h`.

`ansible-playbook <PATH_TO_REPO>/samples/execute_commands.yml -i <PATH_TO_REPO>/samples/hosts`

### Install Packages

[install_packages.yml](/docs/samples/install_packages.yml)

Downloads CentOS image and installs `vim`.

`ansible-playbook <PATH_TO_REPO>/samples/install_packages.yml -i <PATH_TO_REPO>/samples/hosts`

### Modify Usesrs

[modify_users.yml](/docs/samples/modify_users.yml)

Downloads CentOS image and modifies root user's password to `changeme`.

`ansible-playbook <PATH_TO_REPO>/samples/modify_users.yml -i <PATH_TO_REPO>/samples/hosts`

### Fetch File

[copy_out.yml](/docs/samples/copy_out.yml)

Downloads CentOS image and copies `/etc/hosts` from the image.

`ansible-playbook <PATH_TO_REPO>/samples/copy_out.yml -i <PATH_TO_REPO>/samples/hosts`

### Upload File

[copy_in.yml](/docs/samples/copy_in.yml)

Downloads CentOS image and copies `/etc/hosts` from host to the image.

`ansible-playbook <PATH_TO_REPO>/samples/copy_in.yml -i <PATH_TO_REPO>/samples/hosts`
