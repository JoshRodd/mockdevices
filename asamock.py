#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys, locale, socket
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Interface
from datetime import datetime, timezone

SSH_CONN_KEY = 'SSH_CONNECTION'
try:
    ssh_conn = os.environ[SSH_CONN_KEY]
    ssh_conn_l = os.environ[SSH_CONN_KEY].split()
    if len(ssh_conn_l) != 4:
       raise Exception('Environment variable {} is not in the expected `address port address port\' format: {}'.format(SSH_CONN_KEY, ssh_conn))
    remote_ip_addr, remote_port, local_ip_addr, local_port = ssh_conn_l
except KeyError:
    remote_ip_addr, remote_port, local_ip_addr, local_port = '::1', 22, '::1', 22
local_user = getpass.getuser()
enable_password = 'asapass'
local_ip_addr = ipaddress.ip_address(local_ip_addr)
if isinstance(local_ip_addr, IPv6Address):
    if local_ip_addr == IPv6Address('::1'):
        local_ip_addr = IPv4Address('127.0.0.1')
    else:
        raise Exception('IPv6 is not supported other than for loopback addresses like `::1\'.')
local_hostname = socket.getfqdn(str(local_ip_addr))
if local_hostname == str(local_ip_addr):
    raise Exception('Cannot resolve IP address `{}\' to a hostname.'.format(local_ip_addr))

def flush():
    try:
        sys.stdout.flush()
    except:
        pass

# local_ip_addr = ipaddress.IPv4Address('56.0.0.1')
wan_prefixlen = 30
wan_interface = IPv4Interface(str(local_ip_addr) + '/' + str(wan_prefixlen))
wan_network = ip_network(wan_interface.network)
wan_addess = ip_address(wan_interface.ip)

print(wan_prefixlen)
print(wan_network)
print(wan_addess)

#  8         'hostname': hostname or 'asa-site1-9-0-0-0',
#  9         'wan_network': wan_network or '9.0.0.0 255.255.248.0',
# 10         'wan_addess': wan_addess or '9.0.0.0 255.255.255.252',
# 11         'wan_peer': wan_peer or '9.0.0.2 255.255.248.0',
# 12         'mpi_network': mpi_network or '9.128.0.0 255.255.255.128',
# 13         'mpi_address': mpi_address or '9.128.0.1 255.255.255.128',
# 14         'mpe_network': mpe_network or '9.128.0.128 255.255.255.128',
# 15         'mpe_address': mpe_address or '9.128.0.129 255.255.255.128',
# 16         'users_network': users_network or '10.100.0.0 255.255.255.0',
# 17         'users_address': users_address or '10.100.0.1 255.255.255.0',

from asa_config import asa_config
cfg = asa_config.asa_config(local_hostname, wan_network, wan_addess, mpi_address, mpe_address,
                            users_address, users_network, mpe_network, mpi_network, wan_peer)


print('''\

##############################################################################
#                                                                            #
# A typical banner or legal notice goes here.                                #
#                                                                            #
''' + '# {}'.format(local_hostname) + '''
#                                                                            #
##############################################################################
Type help or '?' for a list of available commands.

''', end='');
sys.stdout.flush()

in_enable=False
cur_prompt='>'
no_more=False

while True:
    print('\r{}{} '.format(local_hostname, cur_prompt), end='')
    flush()
    ln = sys.stdin.readline()
    if ln == 'enable\n':
        print('\rPassword: ', end='')
        flush()
        enablepasswordln = sys.stdin.readline()
        if '{}\n'.format(enable_password) != enablepasswordln:
            print('Invalid password.')
        else:
            in_enable=True
            cur_prompt='#'
    elif ln in ('exit\n', 'logout\n', 'quit\n'):
        break
    elif ln == 'terminal pager 0\n':
        no_more=True
        pass
    elif ln == 'show cpu | i util\n':
        print('CPU utilization for 5 seconds = 1%; 1 minute: 1%; 5 minutes: 1%')
    elif ln == 'show clock\n':
        locale.setlocale(locale.LC_TIME, "C")
        print("{:%H:%M:%S.0 %Z %a %b %d %Y}".format(datetime.now(timezone.utc)))
    elif ln == 'show mem\n':
        print('''\
Free memory:        1441865728 bytes (67%)
Used memory:         705617920 bytes (33%)
-------------     ------------------
Total memory:       2147483648 bytes (100%)

Virtual platform memory
-----------------------
Provisioned       2048 MB
Allowed              0 MB
Status            Noncompliant: Over-provisioned
''', end='')
    elif ln == 'show version | i Software Version\n':
        print('''\
Cisco Adaptive Security Appliance Software Version 9.1(7)13
''', end='');
        flush()
    elif ln == 'show cpu\n':
        print('''\
CPU utilization for 5 seconds = 2%; 1 minute: 0%; 5 minutes: 0%

Virtual platform CPU resources
------------------------------
Number of vCPUs              :     1
Number of allowed vCPUs      :     0
vCPU Status                  :  Noncompliant: Over-provisioned
''', end='');
    elif ln == 'show ipv6 access-list\n':
        pass
    else:
        print('''         ^
ERROR: % Invalid input detected at '^' marker.''')
        flush()
print('''\

Logoff

''',end='')
sys.exit(0)
