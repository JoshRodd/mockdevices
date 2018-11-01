#!/usr/bin/env python3

from interactive_asa import ASA
import operator
import pytest
from asa_config import asa_config


EXEC_PROMPT = 'asa-site1-9-0-0-0> '
CONF_STRING = asa_config()
TEST_ASA = ASA(configstr=CONF_STRING)
ENABLE_PROMPT = 'asa-site1-9-0-0-0# '
CONFIG_PROMPT = 'asa-site1-9-0-0-0(config)# '
ICMP_GROUP_PROMPT = 'config-icmp-object-group'
SERVICE_GROUP_PROMPT = 'config-service-object-group'
NETWORK_GROUP_PROMPT = 'config-network-object-group'
SHOW_RUN = '''\
: Saved
:
: Serial Number: 9AJDFJGV165
: Hardware:   ASAv, 2048 MB RAM, CPU Pentium II 2000 MHz
:
ASA Version 9.5(2)204
!
terminal width 511
hostname asa-site1-9-0-0-0
enable password 2KFQnbNIdI.2KYOU encrypted
xlate per-session deny tcp any4 any4
xlate per-session deny tcp any4 any6
xlate per-session deny tcp any6 any4
xlate per-session deny tcp any6 any6
xlate per-session deny udp any4 any4 eq domain
xlate per-session deny udp any4 any6 eq domain
xlate per-session deny udp any6 any4 eq domain
xlate per-session deny udp any6 any6 eq domain
passwd 2KFQnbNIdI.2KYOU encrypted
names
!
interface GigabitEthernet0/0
 description to ** MPLS Uplink **
 duplex full
 nameif outside
 security-level 0
 ip address 9.0.0.1 255.255.255.252
!
interface GigabitEthernet0/1
 description to ** Internal MPI Network **
 duplex full
 nameif MPI
 security-level 100
 ip address 9.128.0.1 255.255.255.128
!
interface GigabitEthernet0/2
 description ** Internal MPE Network **
 duplex full
 nameif MPE
 security-level 90
 ip address 9.128.0.129 255.255.255.128
!
interface GigabitEthernet0/3
 description to ** Internal Users **
 nameif users
 no security-level
 ip address 10.100.0.1 255.255.255.0
!
interface Management0/0
 shutdown
 description to ** MGMT **
 duplex full
 management-only
 nameif mgmt
 security-level 100
 ip address 172.16.1.99 255.255.254.0
!
ftp mode passive
same-security-traffic permit inter-interface
object-group network INTERNAL_USERS
 network-object 10.100.0.0 255.255.255.0
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
 network-object 9.128.0.128 255.255.255.128
object-group network INTERNAL_MPI_SERVERS
 network-object 9.128.0.0 255.255.255.128
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
access-list outside-in remark ### outside-in ACL
access-list outside-in extended permit icmp any any
access-list outside-in extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPE_SERVERS
access-list outside-in extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPI_SERVERS
access-list outside-in extended permit udp host 10.101.70.14 object-group INTERNAL_USERS eq 139
access-list outside-in extended permit tcp 10.101.72.10 255.255.255.254 object-group INTERNAL_USERS eq 445
access-list outside-in extended permit object-group MPI_SERVICES object-group MPI_SERVERS object-group INTERNAL_MPI_SERVERS
access-list outside-in extended permit object-group MPE_SERVICES object-group MPE_SERVERS object-group INTERNAL_MPE_SERVERS
access-list MPE-in remark ### MPE-in ACL
access-list MPE-in extended permit icmp any any
access-list MPE-in extended permit object-group MPE_SERVICES object-group INTERNAL_MPE_SERVERS object-group MPE_SERVERS
access-list MPE-in extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPE_SERVERS
access-list MPE-in extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS
access-list MPI-in remark ### MPI-in ACL
access-list MPI-in extended permit icmp any any
access-list MPI-in extended permit object-group MPI_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPI_SERVERS
access-list users-in remark ### users-in ACL
access-list users-in extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_ORDERING_SERVERS
access-list users-in extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group MPE_SERVERS
access-list users-in extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group INTERNET_SERVERS
access-list users-in extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_USER_SERVICES
pager lines 23
logging enable
logging timestamp
logging monitor debugging
logging asdm informational
logging facility 23
logging host mgmt 10.20.50.103
logging message 106023 level notifications
mtu outside 1500
mtu MPI 1500
mtu MPE 1500
mtu mgmt 1500
no failover
icmp unreachable rate-limit 1 burst-size 1
no asdm history enable
arp timeout 14400
no arp permit-nonconnected
access-group outside-in in interface outside
access-group MPI-in in interface MPI
access-group MPE-in in interface MPE
access-group users-in in interface users
route outside 0.0.0.0 0.0.0.0 9.0.0.2 255.255.248.0  1
timeout xlate 3:00:00
timeout pat-xlate 0:00:30
timeout conn 1:00:00 half-closed 0:10:00 udp 0:02:00 sctp 0:02:00 icmp 0:00:02
timeout sunrpc 0:10:00 h323 0:05:00 h225 1:00:00 mgcp 0:05:00 mgcp-pat 0:05:00
timeout sip 0:30:00 sip_media 0:02:00 sip-invite 0:03:00 sip-disconnect 0:02:00
timeout sip-provisional-media 0:02:00 uauth 0:05:00 absolute
timeout tcp-proxy-reassembly 0:01:00
timeout floating-conn 0:00:00
user-identity default-domain LOCAL
aaa authentication ssh console LOCAL
http server enable
http 0.0.0.0 0.0.0.0 mgmt
http 0.0.0.0 0.0.0.0 outside
http 0.0.0.0 0.0.0.0 MPI
http 0.0.0.0 0.0.0.0 MPE
no snmp-server location
no snmp-server contact
crypto ipsec security-association pmtu-aging infinite
crypto ca trustpoint _SmartCallHome_ServerCA
 no validation-usage
 crl configure
crypto ca trustpool policy
 auto-import
crypto ca certificate chain _SmartCallHome_ServerCA
 certificate ca 6ecc7aa5a7032009b8cebcf4e952d491
    308205ec 308204d4 a0030201 0202106e cc7aa5a7 032009b8 cebcf4e9 52d49130
    0d06092a 864886f7 0d010105 05003081 ca310b30 09060355 04061302 55533117
    30150603 55040a13 0e566572 69536967 6e2c2049 6e632e31 1f301d06 0355040b
    13165665 72695369 676e2054 72757374 204e6574 776f726b 313a3038 06035504
    0b133128 63292032 30303620 56657269 5369676e 2c20496e 632e202d 20466f72
    20617574 686f7269 7a656420 75736520 6f6e6c79 31453043 06035504 03133c56
    65726953 69676e20 436c6173 73203320 5075626c 69632050 72696d61 72792043
    65727469 66696361 74696f6e 20417574 686f7269 7479202d 20473530 1e170d31
    30303230 38303030 3030305a 170d3230 30323037 32333539 35395a30 81b5310b
    30090603 55040613 02555331 17301506 0355040a 130e5665 72695369 676e2c20
    496e632e 311f301d 06035504 0b131656 65726953 69676e20 54727573 74204e65
    74776f72 6b313b30 39060355 040b1332 5465726d 73206f66 20757365 20617420
    68747470 733a2f2f 7777772e 76657269 7369676e 2e636f6d 2f727061 20286329
    3130312f 302d0603 55040313 26566572 69536967 6e20436c 61737320 33205365
    63757265 20536572 76657220 4341202d 20473330 82012230 0d06092a 864886f7
    0d010101 05000382 010f0030 82010a02 82010100 b187841f c20c45f5 bcab2597
    a7ada23e 9cbaf6c1 39b88bca c2ac56c6 e5bb658e 444f4dce 6fed094a d4af4e10
    9c688b2e 957b899b 13cae234 34c1f35b f3497b62 83488174 d188786c 0253f9bc
    7f432657 5833833b 330a17b0 d04e9124 ad867d64 12dc744a 34a11d0a ea961d0b
    15fca34b 3bce6388 d0f82d0c 948610ca b69a3dca eb379c00 48358629 5078e845
    63cd1941 4ff595ec 7b98d4c4 71b350be 28b38fa0 b9539cf5 ca2c23a9 fd1406e8
    18b49ae8 3c6e81fd e4cd3536 b351d369 ec12ba56 6e6f9b57 c58b14e7 0ec79ced
    4a546ac9 4dc5bf11 b1ae1c67 81cb4455 33997f24 9b3f5345 7f861af3 3cfa6d7f
    81f5b84a d3f58537 1cb5a6d0 09e4187b 384efa0f 02030100 01a38201 df308201
    db303406 082b0601 05050701 01042830 26302406 082b0601 05050730 01861868
    7474703a 2f2f6f63 73702e76 65726973 69676e2e 636f6d30 12060355 1d130101
    ff040830 060101ff 02010030 70060355 1d200469 30673065 060b6086 480186f8
    45010717 03305630 2806082b 06010505 07020116 1c687474 70733a2f 2f777777
    2e766572 69736967 6e2e636f 6d2f6370 73302a06 082b0601 05050702 02301e1a
    1c687474 70733a2f 2f777777 2e766572 69736967 6e2e636f 6d2f7270 61303406
    03551d1f 042d302b 3029a027 a0258623 68747470 3a2f2f63 726c2e76 65726973
    69676e2e 636f6d2f 70636133 2d67352e 63726c30 0e060355 1d0f0101 ff040403
    02010630 6d06082b 06010505 07010c04 61305fa1 5da05b30 59305730 55160969
    6d616765 2f676966 3021301f 30070605 2b0e0302 1a04148f e5d31a86 ac8d8e6b
    c3cf806a d448182c 7b192e30 25162368 7474703a 2f2f6c6f 676f2e76 65726973
    69676e2e 636f6d2f 76736c6f 676f2e67 69663028 0603551d 11042130 1fa41d30
    1b311930 17060355 04031310 56657269 5369676e 4d504b49 2d322d36 301d0603
    551d0e04 1604140d 445c1653 44c1827e 1d20ab25 f40163d8 be79a530 1f060355
    1d230418 30168014 7fd365a7 c2ddecbb f03009f3 4339fa02 af333133 300d0609
    2a864886 f70d0101 05050003 82010100 0c8324ef ddc30cd9 589cfe36 b6eb8a80
    4bd1a3f7 9df3cc53 ef829ea3 a1e697c1 589d756c e01d1b4c fad1c12d 05c0ea6e
    b2227055 d9203340 3307c265 83fa8f43 379bea0e 9a6c70ee f69c803b d937f47a
    6decd018 7d494aca 99c71928 a2bed877 24f78526 866d8705 404167d1 273aeddc
    481d22cd 0b0b8bbc f4b17bfd b499a8e9 762ae11a 2d876e74 d388dd1e 22c6df16
    b62b8214 0a945cf2 50ecafce ff62370d ad65d306 4153ed02 14c8b558 28a1ace0
    5becb37f 954afb03 c8ad26db e6667812 4ad99f42 fbe198e6 42839b8f 8f6724e8
    6119b5dd cdb50b26 058ec36e c4c875b8 46cfe218 065ea9ae a8819a47 16de0c28
    6c2527b9 deb78458 c61f381e a4c4cb66
  quit
telnet timeout 15
ssh stricthostkeycheck
ssh 0.0.0.0 0.0.0.0 mgmt
ssh timeout 5
ssh version 2
ssh key-exchange group dh-group14-sha1
console timeout 0
threat-detection basic-threat
threat-detection statistics access-list
no threat-detection statistics tcp-intercept
dynamic-access-policy-record DfltAccessPolicy
username cisco password 3USUcOPFUiMCO4Jk encrypted privilege 15
!
class-map inspection_default
 match default-inspection-traffic
!
!
policy-map type inspect dns preset_dns_map
 parameters
  message-length maximum client auto
  message-length maximum 512
policy-map type inspect dns migrated_dns_map_1
 parameters
  message-length maximum client auto
  message-length maximum 512
policy-map global_policy
 class inspection_default
  inspect ip-options
  inspect netbios
  inspect rtsp
  inspect sunrpc
  inspect tftp
  inspect xdmcp
  inspect ftp
  inspect h323 h225
  inspect h323 ras
  inspect rsh
  inspect esmtp
  inspect sqlnet
  inspect sip
  inspect skinny
  inspect icmp
  inspect http
  inspect dns migrated_dns_map_1
!
service-policy global_policy global
prompt hostname context
no call-home reporting anonymous
call-home
 profile CiscoTAC-1
  no active
  destination address http https://tools.cisco.com/its/service/oddce/services/DDCEService
  destination address email callhome@cisco.com
 profile License
  destination address http https://tools.cisco.com/its/service/oddce/services/DDCEService
  destination transport-method http
Cryptochecksum:89fc0e7a75db639607400231a59c9051
: end'''


def get_config_str():
    return TEST_ASA.config_string


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
        'show_run',
        ('show running-config\n',),
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
access-list outside-in; 14 elements; name hash: 0xedd925e1
access-list outside-in line 1 remark ### outside-in ACL
access-list outside-in line 2 extended permit icmp any any (hitcnt=0) 0x85017d75
access-list outside-in line 3 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x4e3cd4f6
  access-list outside-in line 3 extended permit tcp 71.129.45.34 255.255.255.255 9.128.0.128 255.255.255.128 eq 8443 (hitcnt=0) 0x77e3104f
  access-list outside-in line 3 extended permit udp 71.129.45.34 255.255.255.255 9.128.0.128 255.255.255.128 eq 25 (hitcnt=0) 0x2141bc0b
access-list outside-in line 4 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0xd4866d0d
  access-list outside-in line 4 extended permit tcp 71.129.45.34 255.255.255.255 9.128.0.0 255.255.255.128 eq 8443 (hitcnt=0) 0x8e2db985
  access-list outside-in line 4 extended permit udp 71.129.45.34 255.255.255.255 9.128.0.0 255.255.255.128 eq 25 (hitcnt=0) 0xab808c46
access-list outside-in line 5 extended permit udp host 10.101.70.14 object-group INTERNAL_USERS eq 139 (hitcnt=0) 0x1130d773
  access-list outside-in line 5 extended permit udp host 10.101.70.14 10.100.0.0 255.255.255.0 eq 139 (hitcnt=0) 0x58055ecb
access-list outside-in line 6 extended permit tcp 10.101.72.10 255.255.255.254 object-group INTERNAL_USERS eq 445 (hitcnt=0) 0x2f602989
  access-list outside-in line 6 extended permit tcp 10.101.72.10 255.255.255.254 10.100.0.0 255.255.255.0 eq 445 (hitcnt=0) 0x8f0582a3
access-list outside-in line 7 extended permit object-group MPI_SERVICES object-group MPI_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0x5940d9e8
  access-list outside-in line 7 extended permit tcp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range 1098 1099 (hitcnt=0) 0x2daffadd
  access-list outside-in line 7 extended permit udp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range 1098 1099 (hitcnt=0) 0x5033e7f2
  access-list outside-in line 7 extended permit tcp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range ftp telnet (hitcnt=0) 0x63da26f3
  access-list outside-in line 7 extended permit ah 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 (hitcnt=0) 0x377e42f
  access-list outside-in line 7 extended permit 97 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 (hitcnt=0) 0xb2d60ac5
access-list outside-in line 8 extended permit object-group MPE_SERVICES object-group MPE_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x167d4723
  access-list outside-in line 8 extended permit tcp 10.0.0.128 255.0.0.192 9.128.0.128 255.255.255.128 eq https (hitcnt=0) 0x1462d670
  access-list outside-in line 8 extended permit tcp 10.0.0.128 255.0.0.192 9.128.0.128 255.255.255.128 eq 8443 (hitcnt=0) 0xc8db9204
access-list MPE-in; 15 elements; name hash: 0xb87d96d7
access-list MPE-in line 1 remark ### MPE-in ACL
access-list MPE-in line 2 extended permit icmp any any (hitcnt=0) 0x85017d75
access-list MPE-in line 3 extended permit object-group MPE_SERVICES object-group INTERNAL_MPE_SERVERS object-group MPE_SERVERS (hitcnt=0) 0xd2098745
  access-list MPE-in line 3 extended permit tcp 9.128.0.128 255.255.255.128 10.0.0.128 255.0.0.192 eq https (hitcnt=0) 0xfc2fb94b
  access-list MPE-in line 3 extended permit tcp 9.128.0.128 255.255.255.128 10.0.0.128 255.0.0.192 eq 8443 (hitcnt=0) 0x3d609a43
access-list MPE-in line 4 extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPE_SERVERS (hitcnt=0) 0x60fc7c84
  access-list MPE-in line 4 extended permit tcp 9.128.0.0 255.255.255.128 10.0.0.128 255.0.0.192 eq https (hitcnt=0) 0x32b180ee
  access-list MPE-in line 4 extended permit tcp 9.128.0.0 255.255.255.128 10.0.0.128 255.0.0.192 eq 8443 (hitcnt=0) 0xc2bda034
access-list MPE-in line 5 extended permit object-group MPE_SERVICES object-group INTERNAL_MPI_SERVERS object-group ENCLAVE_MAIL_SERVERS (hitcnt=0) 0x96d7c220
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.51.0 255.255.255.0 eq https (hitcnt=0) 0x794da3c7
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.53.0 255.255.255.0 eq https (hitcnt=0) 0x6c07e8a8
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.55.0 255.255.255.0 eq https (hitcnt=0) 0x53d93519
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.57.0 255.255.255.0 eq https (hitcnt=0) 0x46937e76
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.59.0 255.255.255.0 eq https (hitcnt=0) 0x2c648e7b
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.51.0 255.255.255.0 eq 8443 (hitcnt=0) 0x3a4ace11
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.53.0 255.255.255.0 eq 8443 (hitcnt=0) 0xaa2ce84c
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.55.0 255.255.255.0 eq 8443 (hitcnt=0) 0xc1f784ea
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.57.0 255.255.255.0 eq 8443 (hitcnt=0) 0x5191a2b7
  access-list MPE-in line 5 extended permit tcp 9.128.0.0 255.255.255.128 10.100.59.0 255.255.255.0 eq 8443 (hitcnt=0) 0x16415da6
access-list MPI-in; 6 elements; name hash: 0xf2ab296f
access-list MPI-in line 1 remark ### MPI-in ACL
access-list MPI-in line 2 extended permit icmp any any (hitcnt=0) 0x85017d75
access-list MPI-in line 3 extended permit object-group MPI_SERVICES object-group INTERNAL_MPI_SERVERS object-group MPI_SERVERS (hitcnt=0) 0x43385a58
  access-list MPI-in line 3 extended permit tcp 9.128.0.0 255.255.255.128 10.0.0.192 255.0.0.192 range 1098 1099 (hitcnt=0) 0xa7fe3f12
  access-list MPI-in line 3 extended permit udp 9.128.0.0 255.255.255.128 10.0.0.192 255.0.0.192 range 1098 1099 (hitcnt=0) 0xda62223d
  access-list MPI-in line 3 extended permit tcp 9.128.0.0 255.255.255.128 10.0.0.192 255.0.0.192 range ftp telnet (hitcnt=0) 0x688ba817
  access-list MPI-in line 3 extended permit ah 9.128.0.0 255.255.255.128 10.0.0.192 255.0.0.192 (hitcnt=0) 0xc86e165d
  access-list MPI-in line 3 extended permit 97 9.128.0.0 255.255.255.128 10.0.0.192 255.0.0.192 (hitcnt=0) 0x79cff8b7
access-list users-in; 32 elements; name hash: 0xd013e11d
access-list users-in line 1 remark ### users-in ACL
access-list users-in line 2 extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_ORDERING_SERVERS (hitcnt=0) 0x84a4399c
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.52.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x66db609b
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.54.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xd0f402b1
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.56.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xbd112357
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.58.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x67dbc0a4
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.60.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x66b8b227
  access-list users-in line 2 extended permit udp 10.100.0.0 255.255.255.0 10.100.52.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x17c149b3
  access-list users-in line 2 extended permit udp 10.100.0.0 255.255.255.0 10.100.54.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xa1ee2b99
  access-list users-in line 2 extended permit udp 10.100.0.0 255.255.255.0 10.100.56.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0xcc0b0a7f
  access-list users-in line 2 extended permit udp 10.100.0.0 255.255.255.0 10.100.58.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x16c1e98c
  access-list users-in line 2 extended permit udp 10.100.0.0 255.255.255.0 10.100.60.0 255.255.255.0 range 1098 1099 (hitcnt=0) 0x17a29b0f
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.52.0 255.255.255.0 range ftp telnet (hitcnt=0) 0xfc2eb6cc
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.54.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x27235078
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.56.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x6e27f214
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.58.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x4a499b51
  access-list users-in line 2 extended permit tcp 10.100.0.0 255.255.255.0 10.100.60.0 255.255.255.0 range ftp telnet (hitcnt=0) 0x3ef92ab9
  access-list users-in line 2 extended permit ah 10.100.0.0 255.255.255.0 10.100.52.0 255.255.255.0 (hitcnt=0) 0xc746c9ce
  access-list users-in line 2 extended permit ah 10.100.0.0 255.255.255.0 10.100.54.0 255.255.255.0 (hitcnt=0) 0x60727ec6
  access-list users-in line 2 extended permit ah 10.100.0.0 255.255.255.0 10.100.56.0 255.255.255.0 (hitcnt=0) 0xb44eee01
  access-list users-in line 2 extended permit ah 10.100.0.0 255.255.255.0 10.100.58.0 255.255.255.0 (hitcnt=0) 0xf56a1697
  access-list users-in line 2 extended permit ah 10.100.0.0 255.255.255.0 10.100.60.0 255.255.255.0 (hitcnt=0) 0xf9fc846b
  access-list users-in line 2 extended permit 97 10.100.0.0 255.255.255.0 10.100.52.0 255.255.255.0 (hitcnt=0) 0x2465ac76
  access-list users-in line 2 extended permit 97 10.100.0.0 255.255.255.0 10.100.54.0 255.255.255.0 (hitcnt=0) 0x83511b7e
  access-list users-in line 2 extended permit 97 10.100.0.0 255.255.255.0 10.100.56.0 255.255.255.0 (hitcnt=0) 0x576d8bb9
  access-list users-in line 2 extended permit 97 10.100.0.0 255.255.255.0 10.100.58.0 255.255.255.0 (hitcnt=0) 0x1649732f
  access-list users-in line 2 extended permit 97 10.100.0.0 255.255.255.0 10.100.60.0 255.255.255.0 (hitcnt=0) 0x1adfe1d3
access-list users-in line 3 extended permit object-group MPI_SERVICES object-group INTERNAL_USERS object-group MPE_SERVERS (hitcnt=0) 0x39eec1dc
  access-list users-in line 3 extended permit tcp 10.100.0.0 255.255.255.0 10.0.0.128 255.0.0.192 range 1098 1099 (hitcnt=0) 0x1eebf068
  access-list users-in line 3 extended permit udp 10.100.0.0 255.255.255.0 10.0.0.128 255.0.0.192 range 1098 1099 (hitcnt=0) 0x85686ee7
  access-list users-in line 3 extended permit tcp 10.100.0.0 255.255.255.0 10.0.0.128 255.0.0.192 range ftp telnet (hitcnt=0) 0xd8e225fa
  access-list users-in line 3 extended permit ah 10.100.0.0 255.255.255.0 10.0.0.128 255.0.0.192 (hitcnt=0) 0x6bc00c6b
  access-list users-in line 3 extended permit 97 10.100.0.0 255.255.255.0 10.0.0.128 255.0.0.192 (hitcnt=0) 0xc1c7c250
access-list users-in line 4 extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group INTERNET_SERVERS (hitcnt=0) 0xf6a98968
  access-list users-in line 4 extended permit tcp 10.100.0.0 255.255.255.0 71.129.45.34 255.255.255.255 eq 8080 (hitcnt=0) 0x7109d491
access-list users-in line 5 extended permit object-group USER_SERVICES object-group INTERNAL_USERS object-group ENCLAVE_USER_SERVICES (hitcnt=0) 0xeb593d93
  access-list users-in line 5 extended permit tcp 10.100.0.0 255.255.255.0 10.100.70.160 255.254.255.252 eq 8080 (hitcnt=0) 0x19e14666''',
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
access-list outside-in; 14 elements; name hash: 0xedd925e1
access-list outside-in line 1 remark ### outside-in ACL
access-list outside-in line 2 extended permit icmp any any (hitcnt=0) 0x85017d75
access-list outside-in line 3 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x4e3cd4f6
  access-list outside-in line 3 extended permit tcp 71.129.45.34 255.255.255.255 9.128.0.128 255.255.255.128 eq 8443 (hitcnt=0) 0x77e3104f
  access-list outside-in line 3 extended permit udp 71.129.45.34 255.255.255.255 9.128.0.128 255.255.255.128 eq 25 (hitcnt=0) 0x2141bc0b
access-list outside-in line 4 extended permit object-group INTERNET_SERVICES object-group INTERNET_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0xd4866d0d
  access-list outside-in line 4 extended permit tcp 71.129.45.34 255.255.255.255 9.128.0.0 255.255.255.128 eq 8443 (hitcnt=0) 0x8e2db985
  access-list outside-in line 4 extended permit udp 71.129.45.34 255.255.255.255 9.128.0.0 255.255.255.128 eq 25 (hitcnt=0) 0xab808c46
access-list outside-in line 5 extended permit udp host 10.101.70.14 object-group INTERNAL_USERS eq 139 (hitcnt=0) 0x1130d773
  access-list outside-in line 5 extended permit udp host 10.101.70.14 10.100.0.0 255.255.255.0 eq 139 (hitcnt=0) 0x58055ecb
access-list outside-in line 6 extended permit tcp 10.101.72.10 255.255.255.254 object-group INTERNAL_USERS eq 445 (hitcnt=0) 0x2f602989
  access-list outside-in line 6 extended permit tcp 10.101.72.10 255.255.255.254 10.100.0.0 255.255.255.0 eq 445 (hitcnt=0) 0x8f0582a3
access-list outside-in line 7 extended permit object-group MPI_SERVICES object-group MPI_SERVERS object-group INTERNAL_MPI_SERVERS (hitcnt=0) 0x5940d9e8
  access-list outside-in line 7 extended permit tcp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range 1098 1099 (hitcnt=0) 0x2daffadd
  access-list outside-in line 7 extended permit udp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range 1098 1099 (hitcnt=0) 0x5033e7f2
  access-list outside-in line 7 extended permit tcp 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 range ftp telnet (hitcnt=0) 0x63da26f3
  access-list outside-in line 7 extended permit ah 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 (hitcnt=0) 0x377e42f
  access-list outside-in line 7 extended permit 97 10.0.0.192 255.0.0.192 9.128.0.0 255.255.255.128 (hitcnt=0) 0xb2d60ac5
access-list outside-in line 8 extended permit object-group MPE_SERVICES object-group MPE_SERVERS object-group INTERNAL_MPE_SERVERS (hitcnt=0) 0x167d4723
  access-list outside-in line 8 extended permit tcp 10.0.0.128 255.0.0.192 9.128.0.128 255.255.255.128 eq https (hitcnt=0) 0x1462d670
  access-list outside-in line 8 extended permit tcp 10.0.0.128 255.0.0.192 9.128.0.128 255.255.255.128 eq 8443 (hitcnt=0) 0xc8db9204''',
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
 network-object 10.100.0.0 255.255.255.0
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
 network-object 9.128.0.128 255.255.255.128
object-group network INTERNAL_MPI_SERVERS
 network-object 9.128.0.0 255.255.255.128
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
 service-object esp''',
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
        'exit_config_level',
        ('exit\n',),
        None,
        operator.eq,
        True,
        (TEST_ASA.get_prompt,),
        CONFIG_PROMPT,
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
        'end',
        ('end\n',),
        None,
        operator.eq,
        True,
        (TEST_ASA.get_prompt,),
        ENABLE_PROMPT,
    ),

    (
        'show_run_unchanged',
        ('show running-config\n',),
        SHOW_RUN,
        None,
        None,
        None,
        None,
    ),

    (
        'write memory',
        ('write memory',),
        '''\
Building configuration...
Cryptochecksum: e141b46b e03631fe 797913f9 bdabdff5

%Error copying system:/running-config (No Device)
Error executing command
[FAILED]''',
        None,
        None,
        None,
        None,
    ),

    (
        'exit',
        ('exit',),
        None,
        operator.eq,
        True,
        (TEST_ASA.check_exit,),
        True,
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
