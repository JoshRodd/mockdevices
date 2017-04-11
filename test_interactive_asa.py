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
        (TEST_ASA.get_prompt,),
        ENABLE_PROMPT
    ),

    (
        'config_t',
        ('config terminal\n',),
        None,
        operator.eq,
        True,
        (TEST_ASA.get_prompt,),
        CONFIG_PROMPT
    ),

    (
        'exit_config',
        ('exit\n',),
        None,
        operator.eq,
        True,
        (TEST_ASA.get_prompt,),
        ENABLE_PROMPT,
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
        'show_run',
        ('show runnning-config\n',),
        SHOW_RUN,
        None,
        None,
        None,
        None,
    ),

    (
        'show_access_list',
        ('show access-list\n',),
        '''\
access-list cached ACL log flows: total 0, denied 0 (deny-flow-max 4096)
            alert-interval 300
access-list outside-in; 12 elements; name hash: 0x1b93ec97
access-list outside-in line 1 remark ### outside-in ACL
access-list outside-in line 2 extended permit icmp any any (hitcnt=0) 0x313f65b1
access-list outside-in line 3 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0xb03c15eb
  access-list outside-in line 3 extended permit tcp 71.129.45.34 255.255.255.255 10.10.47.128 255.255.255.192 eq 8443 (hitcnt=0) 0x59be53d3
  access-list outside-in line 3 extended permit udp 71.129.45.34 255.255.255.255 10.10.47.128 255.255.255.192 eq 25 (hitcnt=0) 0x40096a89
access-list outside-in line 4 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0xaa00f565
  access-list outside-in line 4 extended permit tcp 71.129.45.34 255.255.255.255 10.10.47.192 255.255.255.192 eq 8443 (hitcnt=0) 0xb5bc9fb3
  access-list outside-in line 4 extended permit udp 71.129.45.34 255.255.255.255 10.10.47.192 255.255.255.192 eq 25 (hitcnt=0) 0x15b07857
access-list outside-in line 5 extended permit object-group MPI_SERVICES object-group MPI_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0x25d15ad5
  access-list outside-in line 5 extended permit tcp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range 1098 1099 (hitcnt=0) 0x7f10f17
  access-list outside-in line 5 extended permit udp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range 1098 1099 (hitcnt=0) 0x888b7eaf
  access-list outside-in line 5 extended permit tcp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range ftp telnet (hitcnt=0) 0x184153a8
  access-list outside-in line 5 extended permit ah 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 (hitcnt=0) 0x74686146
  access-list outside-in line 5 extended permit 97 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 (hitcnt=0) 0x5c8209d
access-list outside-in line 6 extended permit object-group MPE_SERVICES object-group MPE_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x536b0f4
  access-list outside-in line 6 extended permit tcp 10.0.0.128 255.0.0.192 10.10.47.128 255.255.255.192 eq https (hitcnt=0) 0xaf00ddaa
  access-list outside-in line 6 extended permit tcp 10.0.0.128 255.0.0.192 10.10.47.128 255.255.255.192 eq 8443 (hitcnt=0) 0xa1974bb1
access-list MPE-in; 15 elements; name hash: 0x2a403c1f
access-list MPE-in line 1 remark ### MPE-in ACL
access-list MPE-in line 2 extended permit icmp any any (hitcnt=0) 0xc5f5ece9
access-list MPE-in line 3 extended permit object-group MPE_SERVICES object-group INTERNAL_MPE_SERVERS object-group MPE_SERVERS (hitcnt=0) 0x77ce29ca
  access-list MPE-in line 3 extended permit tcp 10.10.47.128 255.255.255.192 10.0.0.128 255.0.0.192 eq https (hitcnt=0) 0x2e40dd2a
  access-list MPE-in line 3 extended permit tcp 10.10.47.128 255.255.255.192 10.0.0.128 255.0.0.192 eq 8443 (hitcnt=0) 0x5f810665
access-list MPE-in line 4 extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPE_SERVERS (hitcnt=0) 0x3511db6d
  access-list MPE-in line 4 extended permit tcp 10.10.47.192 255.255.255.192 10.0.0.128 255.0.0.192 eq https (hitcnt=0) 0xf45cb217
  access-list MPE-in line 4 extended permit tcp 10.10.47.192 255.255.255.192 10.0.0.128 255.0.0.192 eq 8443 (hitcnt=0) 0x2356eb0e
access-list MPE-in line 5 extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS (hitcnt=0) 0xa76397b7
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.51.0 255.255.255.0 eq https (hitcnt=0) 0xfb12fd6b
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.53.0 255.255.255.0 eq https (hitcnt=0) 0xee58b604
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.55.0 255.255.255.0 eq https (hitcnt=0) 0xd1866bb5
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.57.0 255.255.255.0 eq https (hitcnt=0) 0xc4cc20da
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.59.0 255.255.255.0 eq https (hitcnt=0) 0xae3bd0d7
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.51.0 255.255.255.0 eq 8443 (hitcnt=0) 0x6de0a347
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.53.0 255.255.255.0 eq 8443 (hitcnt=0) 0xfd86851a
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.55.0 255.255.255.0 eq 8443 (hitcnt=0) 0x965de9bc
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.57.0 255.255.255.0 eq 8443 (hitcnt=0) 0x63bcfe1
  access-list MPE-in line 5 extended permit tcp 10.10.47.192 255.255.255.192 10.100.59.0 255.255.255.0 eq 8443 (hitcnt=0) 0x41eb30f0
access-list MPI-in; 39 elements; name hash: 0xb56da783
access-list MPI-in line 1 remark ### MPI-in ACL
access-list MPI-in line 2 extended permit icmp any any (hitcnt=0) 0xa89f27c0
access-list MPI-in line 3 extended permit ip any4 any4 (hitcnt=0) 0x72cd5e2d
access-list MPI-in line 4 extended permit object-group MPI_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPI_SERVERS (hitcnt=0) 0x1d860c92
  access-list MPI-in line 4 extended permit tcp 10.10.47.192 255.255.255.192 10.0.0.192 255.0.0.192 range 1098 1099 (hitcnt=0) 0x39524894
  access-list MPI-in line 4 extended permit udp 10.10.47.192 255.255.255.192 10.0.0.192 255.0.0.192 range 1098 1099 (hitcnt=0) 0xb628392c
  access-list MPI-in line 4 extended permit tcp 10.10.47.192 255.255.255.192 10.0.0.192 255.0.0.192 range ftp telnet (hitcnt=0) 0x6cce2275
  access-list MPI-in line 4 extended permit ah 10.10.47.192 255.255.255.192 10.0.0.192 255.0.0.192 (hitcnt=0) 0x2a892caf
  access-list MPI-in line 4 extended permit 97 10.10.47.192 255.255.255.192 10.0.0.192 255.0.0.192 (hitcnt=0) 0x5b296d74
access-list MPI-in line 5 extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group INTERNET_SERVERS (hitcnt=0) 0xbb049163
  access-list MPI-in line 5 extended permit tcp 10.10.51.0 255.255.255.0 71.129.45.34 255.255.255.255 eq 8080 (hitcnt=0) 0x74c078e7
access-list MPI-in line 6 extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_ORDERING_SERVERS (hitcnt=0) 0x8c6dc5b0
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.52.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xcb252e8
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.54.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xba9d30c2
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.56.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xd7781124
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.58.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xdb2f2d7
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.60.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xcd18054
  access-list MPI-in line 6 extended permit udp 10.10.51.0 255.255.255.0 10.100.52.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x135d1534
  access-list MPI-in line 6 extended permit udp 10.10.51.0 255.255.255.0 10.100.54.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xa572771e
  access-list MPI-in line 6 extended permit udp 10.10.51.0 255.255.255.0 10.100.56.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xc89756f8
  access-list MPI-in line 6 extended permit udp 10.10.51.0 255.255.255.0 10.100.58.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x125db50b
  access-list MPI-in line 6 extended permit udp 10.10.51.0 255.255.255.0 10.100.60.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x133ec788
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.52.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x3548ff78
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.54.0 255.255.255.0 range ftp telnet (hitcnt=0) 0xee4519cc
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.56.0 255.255.255.0 range ftp telnet (hitcnt=0) 0xa741bba0
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.58.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x832fd2e5
  access-list MPI-in line 6 extended permit tcp 10.10.51.0 255.255.255.0 10.100.60.0 255.255.255.0 range ftp telnet (hitcnt=0) 0xf79f630d
  access-list MPI-in line 6 extended permit ah 10.10.51.0 255.255.255.0 10.100.52.0 255.255.255.0 (hitcnt=0) 0xd476b3b6
  access-list MPI-in line 6 extended permit ah 10.10.51.0 255.255.255.0 10.100.54.0 255.255.255.0 (hitcnt=0) 0x734204be
  access-list MPI-in line 6 extended permit ah 10.10.51.0 255.255.255.0 10.100.56.0 255.255.255.0 (hitcnt=0) 0xa77e9479
  access-list MPI-in line 6 extended permit ah 10.10.51.0 255.255.255.0 10.100.58.0 255.255.255.0 (hitcnt=0) 0xe65a6cef
  access-list MPI-in line 6 extended permit ah 10.10.51.0 255.255.255.0 10.100.60.0 255.255.255.0 (hitcnt=0) 0xeaccfe13
  access-list MPI-in line 6 extended permit 97 10.10.51.0 255.255.255.0 10.100.52.0 255.255.255.0 (hitcnt=0) 0xc5b2e1f2
  access-list MPI-in line 6 extended permit 97 10.10.51.0 255.255.255.0 10.100.54.0 255.255.255.0 (hitcnt=0) 0x628656fa
  access-list MPI-in line 6 extended permit 97 10.10.51.0 255.255.255.0 10.100.56.0 255.255.255.0 (hitcnt=0) 0xb6bac63d
  access-list MPI-in line 6 extended permit 97 10.10.51.0 255.255.255.0 10.100.58.0 255.255.255.0 (hitcnt=0) 0xf79e3eab
  access-list MPI-in line 6 extended permit 97 10.10.51.0 255.255.255.0 10.100.60.0 255.255.255.0 (hitcnt=0) 0xfb08ac57
access-list MPI-in line 7 extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_USER_SERVICES (hitcnt=0) 0x4d2a230b
  access-list MPI-in line 7 extended permit tcp 10.10.51.0 255.255.255.0 10.100.70.160 255.254.255.252 eq 8080 (hitcnt=0) 0x14851a5d
access-list MPI-in line 8 extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group MPE_SERVERS (hitcnt=0) 0x3f40d299
  access-list MPI-in line 8 extended permit tcp 10.10.51.0 255.255.255.0 10.0.0.128 255.0.0.192 range 1098 1099 (hitcnt=0) 0xc1668e9f
  access-list MPI-in line 8 extended permit udp 10.10.51.0 255.255.255.0 10.0.0.128 255.0.0.192 range 1098 1099 (hitcnt=0) 0x6aca2fdb
  access-list MPI-in line 8 extended permit tcp 10.10.51.0 255.255.255.0 10.0.0.128 255.0.0.192 range ftp telnet (hitcnt=0) 0xfbe4cf3b
  access-list MPI-in line 8 extended permit ah 10.10.51.0 255.255.255.0 10.0.0.128 255.0.0.192 (hitcnt=0) 0xeb2e1645
  access-list MPI-in line 8 extended permit 97 10.10.51.0 255.255.255.0 10.0.0.128 255.0.0.192 (hitcnt=0) 0xab40bccd
access-list TEST_ACL1; 12 elements; name hash: 0xe0181542
access-list TEST_ACL1 line 1 extended permit object-group SCW_12345_svc_AR1 any object-group SCW_12345_dst_AR1 (hitcnt=0) 0x8829ae83
  access-list TEST_ACL1 line 1 extended permit tcp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0xdb8541af
  access-list TEST_ACL1 line 1 extended permit udp any host 10.1.1.1 eq domain (hitcnt=0) 0x4e64a0f8
  access-list TEST_ACL1 line 1 extended permit udp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0x623fd592
  access-list TEST_ACL1 line 1 extended permit esp any host 10.1.1.1 (hitcnt=0) 0x6a574011
access-list TEST_ACL1 line 2 extended permit object-group SCW_12345_svc_AR2 object-group SCW_12345_src_AR2 object-group SCW_12345_dst_AR2 (hitcnt=0) 0x69c6f540
  access-list TEST_ACL1 line 2 extended permit icmp 10.10.10.200 255.255.255.254 host 10.1.1.1 echo (hitcnt=0) 0x445c8969
  access-list TEST_ACL1 line 2 extended permit icmp 10.0.0.1 255.0.0.255 host 10.1.1.1 echo (hitcnt=0) 0x2766d805
  access-list TEST_ACL1 line 2 extended permit udp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq syslog (hitcnt=0) 0xb203f053
  access-list TEST_ACL1 line 2 extended permit udp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq syslog (hitcnt=0) 0xbe52ba52
  access-list TEST_ACL1 line 2 extended permit tcp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq ldaps (hitcnt=0) 0x3afd1df7
  access-list TEST_ACL1 line 2 extended permit tcp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq ldaps (hitcnt=0) 0x36a304f3
  access-list TEST_ACL1 line 2 extended permit ah 10.10.10.200 255.255.255.254 host 10.1.1.1 (hitcnt=0) 0x6811e928
  access-list TEST_ACL1 line 2 extended permit ah 10.0.0.1 255.0.0.255 host 10.1.1.1 (hitcnt=0) 0x39ef2612
access-list TEST_ACL2; 12 elements; name hash: 0x29f31d6d
access-list TEST_ACL2 line 1 extended permit object-group SCW_12345_svc_AR1 any object-group SCW_12345_dst_AR1 (hitcnt=0) 0x662d4fd2
  access-list TEST_ACL2 line 1 extended permit tcp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0x2a50fecb
  access-list TEST_ACL2 line 1 extended permit udp any host 10.1.1.1 eq domain (hitcnt=0) 0x68db9481
  access-list TEST_ACL2 line 1 extended permit udp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0x93ea6af6
  access-list TEST_ACL2 line 1 extended permit esp any host 10.1.1.1 (hitcnt=0) 0xea0deca4
access-list TEST_ACL2 line 2 extended permit object-group SCW_12345_svc_AR2 object-group SCW_12345_src_AR2 object-group SCW_12345_dst_AR2 (hitcnt=0) 0x97482f3
  access-list TEST_ACL2 line 2 extended permit icmp 10.10.10.200 255.255.255.254 host 10.1.1.1 echo (hitcnt=0) 0xdd1c6e06
  access-list TEST_ACL2 line 2 extended permit icmp 10.0.0.1 255.0.0.255 host 10.1.1.1 echo (hitcnt=0) 0x83185ac0
  access-list TEST_ACL2 line 2 extended permit udp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq syslog (hitcnt=0) 0x441b5c6
  access-list TEST_ACL2 line 2 extended permit udp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq syslog (hitcnt=0) 0x7d775801
  access-list TEST_ACL2 line 2 extended permit tcp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq ldaps (hitcnt=0) 0x1e95b5c8
  access-list TEST_ACL2 line 2 extended permit tcp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq ldaps (hitcnt=0) 0x1fcff60e
  access-list TEST_ACL2 line 2 extended permit ah 10.10.10.200 255.255.255.254 host 10.1.1.1 (hitcnt=0) 0x83bba195
  access-list TEST_ACL2 line 2 extended permit ah 10.0.0.1 255.0.0.255 host 10.1.1.1 (hitcnt=0) 0x38b200c3
access-list TEST_ACL3; 12 elements; name hash: 0x7814a4ed
access-list TEST_ACL3 line 1 extended permit object-group SCW_12345_svc_AR1 any object-group SCW_12345_dst_AR1 (hitcnt=0) 0x3c2eef1d
  access-list TEST_ACL3 line 1 extended permit tcp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0x7ae39417
  access-list TEST_ACL3 line 1 extended permit udp any host 10.1.1.1 eq domain (hitcnt=0) 0x754e8756
  access-list TEST_ACL3 line 1 extended permit udp any host 10.1.1.1 range 1000 10000 (hitcnt=0) 0xc359002a
  access-list TEST_ACL3 line 1 extended permit esp any host 10.1.1.1 (hitcnt=0) 0x95c47737
access-list TEST_ACL3 line 2 extended permit object-group SCW_12345_svc_AR2 object-group SCW_12345_src_AR2 object-group SCW_12345_dst_AR2 (hitcnt=0) 0x9fca525d
  access-list TEST_ACL3 line 2 extended permit icmp 10.10.10.200 255.255.255.254 host 10.1.1.1 echo (hitcnt=0) 0x1cf3311c
  access-list TEST_ACL3 line 2 extended permit icmp 10.0.0.1 255.0.0.255 host 10.1.1.1 echo (hitcnt=0) 0x561d26bc
  access-list TEST_ACL3 line 2 extended permit udp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq syslog (hitcnt=0) 0x698076b5
  access-list TEST_ACL3 line 2 extended permit udp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq syslog (hitcnt=0) 0x8abb040f
  access-list TEST_ACL3 line 2 extended permit tcp 10.10.10.200 255.255.255.254 host 10.1.1.1 eq ldaps (hitcnt=0) 0x2b22ddd
  access-list TEST_ACL3 line 2 extended permit tcp 10.0.0.1 255.0.0.255 host 10.1.1.1 eq ldaps (hitcnt=0) 0xb1c4a59a
  access-list TEST_ACL3 line 2 extended permit ah 10.10.10.200 255.255.255.254 host 10.1.1.1 (hitcnt=0) 0xdadd99fe
  access-list TEST_ACL3 line 2 extended permit ah 10.0.0.1 255.0.0.255 host 10.1.1.1 (hitcnt=0) 0x8ea9e0b3''',
        None,
        None,
        None,
        None,
    ),

    (
        'show_access_list_name',
        ('show access-list outside-in\n',),
        '''\
access-list cached ACL log flows: total 0, denied 0 (deny-flow-max 4096)
            alert-interval 300
access-list outside-in; 12 elements; name hash: 0x1b93ec97
access-list outside-in line 1 remark ### outside-in ACL
access-list outside-in line 2 extended permit icmp any any (hitcnt=0) 0x313f65b1
access-list outside-in line 3 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0xb03c15eb
  access-list outside-in line 3 extended permit tcp 71.129.45.34 255.255.255.255 10.10.47.128 255.255.255.192 eq 8443 (hitcnt=0) 0x59be53d3
  access-list outside-in line 3 extended permit udp 71.129.45.34 255.255.255.255 10.10.47.128 255.255.255.192 eq 25 (hitcnt=0) 0x40096a89
access-list outside-in line 4 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0xaa00f565
  access-list outside-in line 4 extended permit tcp 71.129.45.34 255.255.255.255 10.10.47.192 255.255.255.192 eq 8443 (hitcnt=0) 0xb5bc9fb3
  access-list outside-in line 4 extended permit udp 71.129.45.34 255.255.255.255 10.10.47.192 255.255.255.192 eq 25 (hitcnt=0) 0x15b07857
access-list outside-in line 5 extended permit object-group MPI_SERVICES object-group MPI_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0x25d15ad5
  access-list outside-in line 5 extended permit tcp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range 1098 1099 (hitcnt=0) 0x7f10f17
  access-list outside-in line 5 extended permit udp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range 1098 1099 (hitcnt=0) 0x888b7eaf
  access-list outside-in line 5 extended permit tcp 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 range ftp telnet (hitcnt=0) 0x184153a8
  access-list outside-in line 5 extended permit ah 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 (hitcnt=0) 0x74686146
  access-list outside-in line 5 extended permit 97 10.0.0.192 255.0.0.192 10.10.47.192 255.255.255.192 (hitcnt=0) 0x5c8209d
access-list outside-in line 6 extended permit object-group MPE_SERVICES object-group MPE_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x536b0f4
  access-list outside-in line 6 extended permit tcp 10.0.0.128 255.0.0.192 10.10.47.128 255.255.255.192 eq https (hitcnt=0) 0xaf00ddaa
  access-list outside-in line 6 extended permit tcp 10.0.0.128 255.0.0.192 10.10.47.128 255.255.255.192 eq 8443 (hitcnt=0) 0xa1974bb1''',
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
 network-object host 10.1.1.1''',
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
 service-object 97''',
        None,
        None,
        None,
        None,
    ),

    (
        'config_t',
        ('config terminal\n',),
        None,
        operator.eq,
        True,
        (TEST_ASA.get_prompt,),
        CONFIG_PROMPT
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
        ('''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',),
        get_config_str,
    ),

    (
        'add_access_list',
        ('access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2\n',),
        None,
        operator.contains,
        True,
        ('access-list MPE-in extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2',),
        get_config_str,
    ),

    (
        'add_access_list_line',
        ('access-list MPE-in line 2 extended permit ip 10.101.20.54 255.255.255.254 any',),
        None,
        operator.contains,
        True,
        ('''\
access-list MPE-in remark ### MPE-in ACL
access-list MPE-in extended permit ip 10.101.20.54 255.255.255.254 any
access-list MPE-in extended permit icmp any any
''',),
        get_config_str,
    ),

    (
        'no_access_list_line',
        ('no access-list MPE-in line 2',),
        None,
        operator.contains,
        False,
        ('''\
access-list MPE-in extended permit ip 10.101.20.54 255.255.255.254 any
''',),
        get_config_str,
    ),

    (
        'no_object_group_in_use',
        ('no object-group network ENCLAVE_MAIL_SERVERS_2\n',),
        'Removing object-group (ENCLAVE_MAIL_SERVERS_2) not allowed, it is being used.',
        operator.contains,
        True,
        ('''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',),
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
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS_2',),
        get_config_str,
    ),

    (
        'no_object_group',
        ('no object-group network ENCLAVE_MAIL_SERVERS_2\n',),
        None,
        operator.contains,
        False,
        ('''\
object-group network ENCLAVE_MAIL_SERVERS_2
 network-object 10.101.51.0 255.255.255.0
 network-object 10.101.53.0 255.255.255.0
 network-object 10.101.55.0 255.255.255.0
 network-object 10.101.57.0 255.255.255.0
 network-object 10.101.59.0 255.255.255.0
''',),
        get_config_str,
    ),

    (
        'add_object_group_service',
        ('object-group service MPI_SERVICES_2\n',
         ' service-object tcp destination range 2000 2002\n',
         ' service-object udp destination range 2004 2006\n',
         ' service-object tcp destination range ssh\n',
         ' service-object igmp\n',
         ' service-object 98\n',
         ),
        None,
        operator.contains,
        True,
        ('''\
object-group service MPI_SERVICES_2
 service-object tcp destination range 2000 2002
 service-object udp destination range 2004 2006
 service-object tcp destination range ssh
 service-object igmp
 service-object 98
''',),
        get_config_str,
    ),

    (
        'no_object_group_service',
        ('no object-group service MPI_SERVICES_2\n',),
        None,
        operator.contains,
        False,
        ('object-group service MPI_SERVICES_2\n',
         ' service-object tcp destination range 2000 2002\n',
         ' service-object udp destination range 2004 2006\n',
         ' service-object tcp destination range ssh\n',
         ' service-object igmp\n',
         ' service-object 98\n',),
        get_config_str,
    ),

    (
        'add_bogus_object_access-list',
        ('access-list MPE-in extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group BOGUS_BS\n',),
        'ERROR: specified object group <BOGUS_BS> not found',
        None,
        None,
        None,
        None,
    ),

    (
        'no_bogus_access-list',
        ('no access-list BOGUS extended permit object-group MPE_SERVICES '
         'object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS\n',),
        'ERROR: access-list <BOGUS> does not exist',
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
        (TEST_ASA.get_prompt,),
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
        for r in result:
            assert op(known() if callable(known) else known, r() if callable(r) else r) == asrt

    else:
        for c in command:
            assert TEST_ASA.send(c) == (ret() if callable(ret) else ret)
