# mockdevices v1.0
Mocks of various kinds of networking devices.

## Installation

Run the setup_mockdevices-1.0.run script like this:

`/bin/sh setup_mockevices-1.0.run`

To uninstall, either run the script like this:

`/bin/sh setup_mockdevices-1.0.run --uninstall`

Or else run `mockdevices_check_install --uninstall`.

## Prerequisites

Run the `mockdevices_check_install.sh` script to check for a proper installation.
The script will show the commands needed to repair an improper
installation.

A number of RPMs and PIP packages are prerequisites. The check install script
will show the exact details of what they are and how to install them.

You will need to retrieve EPEL from <https://fedoraproject.org/wiki/EPEL>

Python 3.4 cannot be present and must be uninstalled to use this package. The
Python 3.6 packages provided by EPEL will be a suitable replacement in most
scenarios.

If your host does not have Internet access, the necessary RPMs and Python
PIP packages will have to be manually transferred and installed. In particular,
EPEL is required.

## Building

To create a package, run: make && make package

To install directly: make && make install

A file with a name like setup_mockdevices-1.0.run will be created.
