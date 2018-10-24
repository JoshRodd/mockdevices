# mockdevices
Mocks of various kinds of networking devices.

The script `ifconfig-loopbacks` will configure your loopback
interface with lots of IP addresses, which is useful for
testing. For more usage information, use the `--help` option.

To set up, run make && make install. To remove, run make uninstall.

You will need to install xinetd to use multiple ports, which is
easier than using lots of loopback IP addresses. Use
deploy-xinetd.sh to do that. You can then access the mocked device
with telnet.

You will need to deploy a user called "asa" as a standard user.
The configuration files and logs will be placed into that home
directory.
