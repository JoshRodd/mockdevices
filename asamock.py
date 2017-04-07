#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys

SSH_CONN_KEY = 'SSH_CONNECTION'
HOST_PREFIX = 'Asa-'
host_prefix = HOST_PREFIX
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
if isinstance(local_ip_addr, ipaddress.IPv6Address):
    if local_ip_addr == ipaddress.IPv6Address('::1'):
        local_ip_addr = ipaddress.IPv4Address('127.0.0.1')
    else:
        raise Exception('IPv6 is not supported other than for loopback addresses like `::1\'.')
local_ip_addr_str = str(local_ip_addr).replace('.','_')
local_hostname = host_prefix + local_ip_addr_str

def flush():
    try:
        sys.stdout.flush()
    except:
        pass

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

while True:
    print('\r{}{} '.format(local_hostname, cur_prompt), end='')
    flush()
    ln = sys.stdin.readline()
    if ln == 'enable\n':
        print('\rPassword: ', end='')
        flush()
        enablepasswordln = sys.stdin.readline()
        if format('{}'\n', enable_password) != enablepasswordln:
            
        else:
            in_enable=True
            cur_prompt='#'
    elif ln == 'exit\n':
        break
    elif ln == 'terminal pager 0\n':
        pass
    elif ln == 'show version | i Software Version\n':
        print('''\
Cisco Adaptive Security Appliance Software Version 9.1(7)13
''', end='');
        flush()
    else:
        print('''         ^
ERROR: % Invalid input detected at '^' marker.''')
        flush()
print('''\

Logoff

''',end='')
sys.exit(0)
