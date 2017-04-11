#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys, socket

SSH_CONN_KEY = 'SSH_CONNECTION'
remote_ip_addr, remote_port, local_ip_addr, local_port = '::1', 22, '::1', 22
ssh_conn = os.environ[SSH_CONN_KEY]
ssh_conn_l = os.environ[SSH_CONN_KEY].split()
if len(ssh_conn_l) != 4:
    raise Exception('Environment variable {} is not in the expected `address port address port\' format: {}'.format(SSH_CONN_KEY, ssh_conn))
remote_ip_addr, remote_port, local_ip_addr, local_port = ssh_conn_l
local_user = getpass.getuser()
local_password = 'joshpass'
local_ip_addr = ipaddress.ip_address(local_ip_addr)
if isinstance(local_ip_addr, ipaddress.IPv6Address):
    if local_ip_addr == ipaddress.IPv6Address('::1'):
        local_ip_addr = ipaddress.IPv4Address('127.0.0.1')
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

#print(# '{}@{}\'s password: {}'.format(local_user, local_ip_addr, local_password) + '''
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

cur_prompt='>'

while True:
    print('\r{}{} '.format(local_hostname, cur_prompt), end='')
    flush()
    ln = sys.stdin.readline()
    if ln == 'enable\n':
        cur_prompt='#'
        print('\rPassword: ', end='')
        flush()
        enablepasswordln = sys.stdin.readline()
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
