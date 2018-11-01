# mockdevices v1.0
Mocks of various kinds of networking devices.

To set up, run make && make install.

To distribute, run make dist and then distribute the 
`mockdevices_dist.tar.bz2` file. By default it will unpack to `/usr/local/bin`.

Run the `mockdevices_check_install.sh` script to check for a proper installation.
The script will show the commands needed to repair an improper
installation.

A number of RPMs and PIP packages are prerequisites. The check install script
will show the exact details of what they are and how to install them.
