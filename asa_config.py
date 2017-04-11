#!/usr/bin/env python3

from jinja2 import Environment


def template(hostname=None, wan_network=None, wan_addess=None, mpi_address=None, mpe_address=None,
             users_address=None, users_network=None, mpe_network=None, mpi_network=None, wan_peer=None):
    fields = {
        'hostname': hostname or 'asa-site1-9-0-0-0',
        'wan_network': wan_network or '9.0.0.0 255.255.248.0',
        'wan_addess': wan_addess or '9.0.0.0 255.255.255.252',
        'wan_peer': wan_peer or '9.0.0.2 255.255.248.0',
        'mpi_network': mpi_network or '9.128.0.0 255.255.255.128',
        'mpi_address': mpi_address or '9.128.0.1 255.255.255.128',
        'mpe_network': mpe_network or '9.128.0.128 255.255.255.128',
        'mpe_address': mpe_address or '9.128.0.129 255.255.255.128',
        'users_network': users_network or '10.100.0.0 255.255.255.0',
        'users_address': users_address or '10.100.0.1 255.255.255.0',
    }
    with open('baseline_asa.conf') as cfg:
        env = Environment()
        t = env.from_string(cfg.read())
    return t.render(fields)


print(template())
