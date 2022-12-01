# libguestfs Collection

**NOTE:** This collection is not endorsed by the [libguestfs](https://libguestfs.org) community, this is a personal effort.

libguestfs modules allow users to use Ansible to automate commonly used libguestfs actions in a native way.

## Prerequisites:

On Ansible Controller:

- Ansible >= 2.8.0 (May work on earlier releases)
- Python >= 2.7.5 || Python >= 3.4
- gcc

On Ansible Host:

- gcc
- libguestfs
- libguestfs-devel
- Python >= 2.7.5 || Python >= 3.4
- libguestfs python bindings:
    - System:
      If your distribution's package manager contains `python-libguestfs`, install it (via `yum`, `apt` ...)
    - pip:
      If a virtual environment is used or you do not have a pre packaged `python-libguestfs`, refer to [guestfs python bindings in a virtualenv](http://libguestfs.org/guestfs-python.3.html#using-python-bindings-in-a-virtualenv)
      In order to install via pip download the relevant version from `http://download.libguestfs.org/python/`
      Example, `https://download.libguestfs.org/python/guestfs-1.40.2.tar.gz`

## Compatibility Matrix

| Distro             | Supported  | Notes           |
|:------------------:|:-----------|:---------------:|
| Fedora/CentOS/RHEL | Yes        |                 |
| Ubuntu             | Yes        |                 |
| Debian             | Yes        |                 |
| Windows            | No         |  Not Supported  |

## Documentation

Please refer to [docs](/docs) directory.

## Installation

## License

This project is licensed under GPL-3.0 License. Please see the [COPYING.md](/COPYING.md) for more information.
