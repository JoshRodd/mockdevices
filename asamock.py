#!/usr/bin/env python3

import os, re, ipaddress, getpass

SSH_CONN_KEY = 'SSH_CONNECTION'
ssh_conn = os.environ[SSH_CONN_KEY]
ssh_conn_l = os.environ[SSH_CONN_KEY].split()
if len(ssh_conn_l) != 4:
    raise Exception('Environment variable {} is not in the expected `address port address port\' format: {}'.format(SSH_CONN_KEY, ssh_conn))
remote_ip_addr, remote_port, local_ip_addr, local_port = ssh_conn_l
local_user = getpass.getuser()
local_password = 'joshpass'

print(\
"{}@{}'s password: {}".format(local_user, local_ip_addr, local_password) + '''

#########################################################################################
''', end='')
