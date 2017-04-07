#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys

SSH_CONN_KEY = 'SSH_CONNECTION'
HOST_PREFIX = 'Asa-'
host_prefix = HOST_PREFIX
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
local_ip_addr_str = str(local_ip_addr).replace('.','_')
local_hostname = host_prefix + local_ip_addr_str

print(\
'{}@{}\'s password: {}'.format(local_user, local_ip_addr, local_password) + '''

##############################################################################
#                                                                            #
# A typical banner or legal notice goes here.                                #
#                                                                            #
''' + '# {}'.format(local_hostname) + '''
#                                                                            #
##############################################################################
Type help or '?' for a list of available commands.
''' + '\r{}> '.format(local_hostname), end='')
sys.stdout.flush()
ln = sys.stdin.readline()
if ln == 'enable\n':
    print('ok')
else:
    print('invalid command')
