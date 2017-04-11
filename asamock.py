#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys, locale, socket
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Interface
from datetime import datetime, timezone
from collections import defaultdict

SSH_CONN_KEY = 'SSH_CONNECTION'
try:
    ssh_conn = os.environ[SSH_CONN_KEY]
    ssh_conn_l = os.environ[SSH_CONN_KEY].split()
    if len(ssh_conn_l) != 4:
       raise Exception('Environment variable {} is not in the expected `address port address port\' format: {}'.format(SSH_CONN_KEY, ssh_conn))
    remote_ip_addr, remote_port, local_ip_addr, local_port = ssh_conn_l
except KeyError:
#    remote_ip_addr, remote_port, local_ip_addr, local_port = '::1', 22, '::1', 22
    remote_ip_addr, remote_port, local_ip_addr, local_port = '56.0.0.5', 22, '56.0.0.5', 22
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

siteid = int(re.search(r"site(\d+)", local_hostname).group(1))
kwds = {}
prefixlen = {}
ntwks_base = {}
ntwks = {}
ifaces = {}
peers = {}
offsets = {}
prefixlen_noncontig = defaultdict(lambda: 0)
prefixlen['wan'] = 30
prefixlen['mpi'] = 25
prefixlen_noncontig['mpi'] = 1
prefixlen['mpe'] = 25
prefixlen_noncontig['mpe'] = 1
prefixlen['users'] = 24
offsets['mpi'] = '0.128.0.0'
offsets['mpe'] = '0.128.0.128'
wan_interface = IPv4Interface(str(local_ip_addr) + '/' + str(prefixlen['wan']))
ifaces['wan'] = wan_interface.network.with_netmask.replace('/', ' ')
peers['wan'] = ip_address(wan_interface.ip) + 1

wan_classa = IPv4Interface(str(local_ip_addr) + '/8').network.network_address
wan_classa_base = wan_classa + ((siteid - 1) * pow(2, 32 - prefixlen['wan']))
assert wan_classa_base == wan_interface.network.network_address

bases = {}
bases['users'] = '10.100.0.0'

interface_list = ['wan', 'mpe', 'mpi', 'users']

ntwks_base['wan'] = ip_address(str(wan_classa))
ntwks_base['mpi'] = ip_address(str(wan_classa + int(ip_address(offsets['mpi']))))
ntwks_base['mpe'] = ip_address(str(wan_classa + int(ip_address(offsets['mpe']))))
ntwks_base['users'] = ip_address(bases['users'])

for iface in ntwks_base:
    ntwks[iface] = ntwks_base[iface] + ((siteid - 1) * pow(2, 32 - prefixlen[iface] + prefixlen_noncontig[iface]))

for iface in ntwks:
    ifaces[iface] = IPv4Interface(str(ntwks[iface] + 1) + '/' + str(prefixlen[iface])).with_netmask.replace('/', ' ')

for iface in ntwks:
    ntwks[iface] = IPv4Interface(str(ntwks[iface]) + '/' + str(prefixlen[iface])).with_netmask.replace('/', ' ')


kwds = {
    'hostname':         local_hostname,
    'wan_network':      ntwks['wan'],
    'wan_address':      ifaces['wan'],
    'wan_peer':         peers['wan'],
    'mpi_network':      ntwks['mpi'],
    'mpi_address':      ifaces['mpi'],
    'mpe_network':      ntwks['mpe'],
    'mpe_address':      ifaces['mpe'],
    'users_network':    ntwks['users'],
    'users_address':    ifaces['users'],
}

from asa_config import asa_config
cfg = asa_config(**kwds)


motd = '''\

##############################################################################
#                                                                            #
# A typical banner or legal notice goes here.                                #
#                                                                            #
''' + '# {}'.format(local_hostname) + '''
#                                                                            #
##############################################################################
Type help or '?' for a list of available commands.

'''

print(motd, end='')

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
    elif ln == 'mock dump\n':
        print(cfg)
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
