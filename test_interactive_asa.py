#!/usr/bin/env python3

from interactive_asa import ASA
import operator
import pytest


EXEC_PROMPT = 'asav-1> '
CONF_FILE = 'test_asa.conf'
TEST_ASA = ASA(CONF_FILE)
ENABLE_PROMPT = 'asav-1# '
CONFIG_PROMPT = 'asav-1(config)# '
ICMP_GROUP_PROMPT = 'config-icmp-object-group'
SERVICE_GROUP_PROMPT = 'config-service-object-group'
NETWORK_GROUP_PROMPT = 'config-network-object-group'
SHOW_RUN = open('test_asa.conf').read()


def get_config_str():
    return open('test_asa.conf').read()


SENDS = [
    (
        'enable',
        ('enable\n',),
        None,
        operator.eq,
        True,
        TEST_ASA.get_prompt,
        ENABLE_PROMPT
    ),

    (
        'config_t',
        ('config terminal\n',),
        None,
        operator.eq,
        True,
        TEST_ASA.get_prompt,
        CONFIG_PROMPT
    ),

    (
        'show_run',
        ('show runnning-config\n',),
        SHOW_RUN,
        None,
        None,
        None,
        None,
    ),

    (
        'exit',
        ('exit',),
        1,
        None,
        None,
        None,
        None,
    ),

    (
        'show_access_list',
        ('show access-list\n',),
        '''\,
        ''',
        None,
        None,
        None,
        None,
    ),

    (
        'show_access_list_name',
        ('show access-list outside-in\n',),
        '''\
        ''',
        None,
        None,
        None,
        None,
    ),

    (
        'show_object_group',
        ('show object-group\n',),
        '''\
object-group network INTERNAL_USERS
 network-object 10.10.51.0 255.255.255.0
object-group network ENCLAVE_USER_SERVICES
 network-object 10.100.70.160 255.254.255.252
object-group network INTERNET_SERVERS
 network-object 71.129.45.34 255.255.255.255
object-group network ENCLAVE_MAIL_SERVERS
 network-object 10.100.51.0 255.255.255.0
 network-object 10.100.53.0 255.255.255.0
 network-object 10.100.55.0 255.255.255.0
 network-object 10.100.57.0 255.255.255.0
 network-object 10.100.59.0 255.255.255.0
object-group network ENCLAVE_ORDERING_SERVERS
 network-object 10.100.52.0 255.255.255.0
 network-object 10.100.54.0 255.255.255.0
 network-object 10.100.56.0 255.255.255.0
 network-object 10.100.58.0 255.255.255.0
 network-object 10.100.60.0 255.255.255.0
object-group network INTERNAL_MPE_SERVERS
 network-object 10.10.47.128 255.255.255.192
object-group network INTERNAL_MPI_SERVERS
 network-object 10.10.47.192 255.255.255.192
object-group network MPE_SERVERS
 network-object 10.0.0.128 255.0.0.192
object-group network MPI_SERVERS
 network-object 10.0.0.192 255.0.0.192
object-group service MPI_SERVICES
 service-object tcp destination range 1098 1099
 service-object udp destination range 1098 1099
 service-object tcp destination range ftp telnet
 service-object ah
 service-object 97
object-group service MPE_SERVICES
 service-object tcp destination eq https
 service-object tcp destination eq 8443
object-group service INTERNET_SERVICES
 service-object tcp destination eq 8443
 service-object udp destination eq 25
object-group service USER_SERVICES
 service-object tcp destination eq 8080
object-group service SCW_12345_svc_AR1
 service-object tcp destination range 1000 10000
 service-object udp destination eq domain
 service-object udp destination range 1000 10000
 service-object esp
object-group network SCW_12345_dst_AR1
 network-object host 10.1.1.1
object-group service SCW_12345_svc_AR2
 service-object icmp echo
 service-object udp destination eq syslog
 service-object tcp destination eq ldaps
 service-object ah
object-group network SCW_12345_src_AR2
 network-object 10.10.10.200 255.255.255.254
 network-object 10.0.0.1 255.0.0.255
object-group network SCW_12345_dst_AR2
 network-object host 10.1.1.1
''',
        None,
        None,
        None,
        None,
    ),

    (
        'show_object_group_id',
        ('show object-group id MPI_SERVICES',),
        '''\
object-group service MPI_SERVICES
 service-object tcp destination range 1098 1099
 service-object udp destination range 1098 1099
 service-object tcp destination range ftp telnet
 service-object ah
 service-object 97
''',
        None,
        None,
        None,
        None,
    ),

    (
        'add_object_group_network',
        ('object-group network ENCLAVE_MAIL_SERVERS_2\n',
         ' network-object 10.101.51.0 255.255.255.0\n',
         ' network-object 10.101.53.0 255.255.255.0\n',
         ' network-object 10.101.55.0 255.255.255.0\n',
         ' network-object 10.101.57.0 255.255.255.0\n',
         ' network-object 10.101.59.0 255.255.255.0\n',
         ),
        None,
        operator.contains,
        True,
        '''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',
        get_config_str,
    ),

    (
        'add_access_list',
        ('access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2\n',),
        None,
        operator.contains,
        True,
        ('access-list MPE-in extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2'),
        get_config_str,
    ),

    (
        'no_object_group_in_use',
        ('no object-group network ENCLAVE_MAIL_SERVERS_2\n',),
        'Removing object-group (ENCLAVE_MAIL_SERVERS_2) not allowed, it is being used.',
        operator.contains,
        True,
        '''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',
        get_config_str,
    ),

    (
        'no_access_list',
        ('no access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2\n',),
        None,
        operator.contains,
        False,
        ('access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2'),
        get_config_str,
    ),

    (
        'no_object_group',
        ('no object-group network ENCLAVE_MAIL_SERVERS_2\n',),
        None,
        operator.contains,
        False,
        '''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',
        get_config_str,
    ),

    (
        'add_object_group_service',
        ('object-group service MPI_SERVICES_2\n',
         ' service-object tcp destination range 2000 2002\n',
         ' service-object udp destination range 2004 2006\n',
         ' service-object tcp destination range ssh\n',
         ' service-object esp\n',
         ' service-object 98\n',
         ),
        None,
        operator.contains,
        True,
        '''\
object-group service MPI_SERVICES_2
 service-object tcp destination range 2000 2002
 service-object udp destination range 2004 2006
 service-object tcp destination range ssh
 service-object esp
 service-object 98
''',
        get_config_str,
    ),

    (
        'no_object_group_service',
        ('no object-group service MPI_SERVICES_2\n',),
        None,
        operator.contains,
        False,
        '''\
object-group service MPI_SERVICES_2
 service-object tcp destination range 2000 2002
 service-object udp destination range 2004 2006
 service-object tcp destination range ssh
 service-object esp
 service-object 98
''',
        get_config_str,
    ),

    (
        'add_bogus_access-list',
        ('access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group BOGUS_BS\n',),
        'ERROR: specified object group <BOGUS> not found',
        None,
        None,
        None,
        None,
    ),

    (
        'no_bogus_access-list',
        ('no access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group BOGUS_BS\n',),
        None,
        None,
        None,
        None,
        None,
    ),

    (
        'end',
        ('end\n',),
        None,
        operator.eq,
        True,
        TEST_ASA.get_prompt,
        ENABLE_PROMPT,
    ),
]


def test_get_prompt():
    assert EXEC_PROMPT == TEST_ASA.get_prompt()


@pytest.mark.parametrize('name,command,ret,op,asrt,result,known', SENDS, ids=[s[0] for s in SENDS])
def test_sends(name, command, ret, op, asrt, result, known):
    if op:
        for c in command:
            assert TEST_ASA.send(c) == ret
        assert op(known() if callable(known) else known, result() if callable(result) else result) == asrt

    else:
        for c in command:
            assert TEST_ASA.send(c) == ret() if callable(ret) else ret
