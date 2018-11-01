#!/usr/bin/env python3

# Requires:
# psutil
# ifaddr>=0.1.4
# toml>=0.10.0

# Create a file in /opt/tufin/ngps/conf.txt like this:
#
# sshd_ports = [ 22 ]
# sshd_port_ranges = [ [22001, 22999] ]
#
# This says to expect incoming connections on ports 22 and ports
# from 22001 through and including 22999.

import psutil, os, ifaddr, toml

def get_sshd_port(port_list=None, ip_list=None):
    if ip_list is None:
        ip_list = []
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                if isinstance(ip.ip, str):
                    ip_list.append(str(ip.ip))
    if port_list is None:
        try:      
            conf = toml.load("/opt/tufin/ngps/conf.txt")
            port_list = set(conf['sshd_ports'])
            for port_range in conf['sshd_port_ranges']:
                port_list = port_list.union(set(range(port_range[0], port_range[1] + 1)))
        except:
            pass
    sshd_port = 0
    this_p = psutil.Process(os.getpid())
    last_pid = -1
    found = False
    while this_p.pid != 1 and this_p.ppid != 0:
        last_pid = this_p.pid
        if this_p.name() == 'sshd':
            found = True
            sshd_pid = this_p.pid
            break
        this_p = psutil.Process(this_p.ppid())
    if found:
        found = 0
        for pc in [x for x in this_p.connections() if x.status == psutil.CONN_ESTABLISHED]:
            if port_list is not None:
                if pc.laddr.ip in ip_list and pc.laddr.port in port_list:
                    found += 1
            else:
                if pc.laddr.ip in ip_list and pc.laddr.port > 0:
                    found += 1
        if found == 1:
            sshd_port = pc.laddr.port
    return sshd_port

if __name__ == "__main__":
    print(get_sshd_port())
