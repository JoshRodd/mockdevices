#!/usr/bin/env python3

import os, re, getpass, ipaddress, sys, locale, socket
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Interface
from datetime import datetime, timezone
from collections import defaultdict
from interactive_asa import ASA
from asa_config import asa_config
from os.path import expanduser
import readline
import contextlib
import io
import warnings
import termios
import tty
import prompt_toolkit

MORE_STRING = '<--- More --->'

def asa_getpass(prompt='Password: ', stream=sys.stdout, inpu=sys.stdin, echochar='*'):
    """Prompt for a password, with echo turned off, and echo asterisks.
    Args:
      prompt: Written on stream to ask for the input.  Default: 'Password: '
      stream: A writable file object to display the prompt.  Defaults to
              the tty.  If no tty is available defaults to sys.stderr.
    Returns:
      The seKr3t input.
    Raises:
      EOFError: If our input tty or stdin was closed.
      GetPassWarning: When we were unable to turn echo off on the input.
    Always restores terminal settings before returning.
    """
    passwd = None
    fd = stream.fileno()

    if fd is not None:
        try:
            if inpu.isatty() and stream.isatty():
                old = termios.tcgetattr(fd)     # a copy to save
                new = old[:]
                new[3] &= ~termios.ECHO  # 3 == 'lflags'
                tcsetattr_flags = termios.TCSAFLUSH
                if hasattr(termios, 'TCSASOFT'):
                    tcsetattr_flags |= termios.TCSASOFT
            try:
                if inpu.isatty() and stream.isatty():
                    termios.tcsetattr(fd, tcsetattr_flags, new)
                passwd = _raw_input(prompt, stream, inpu, echochar)
            finally:
                if inpu.isatty() and stream.isatty():
                    termios.tcsetattr(fd, tcsetattr_flags, old)
                stream.flush()  # issue7208
        except termios.error:
            if passwd is not None:
                # _raw_input succeeded.  The final tcsetattr failed.  Reraise
                # instead of leaving the terminal in an unknown state.
                raise
    stream.write('\n')
    stream.flush()
    return passwd

def _raw_input(prompt="", stream=sys.stdout, inpu=sys.stdin, echochar=None):
    # This doesn't save the string in the GNU readline history.
    prompt = str(prompt)
    if prompt:
        try:
            stream.write(prompt)
        except UnicodeEncodeError:
            # Use replace error handler to get as much as possible printed.
            prompt = prompt.encode(stream.encoding, 'replace')
            prompt = prompt.decode(stream.encoding)
            stream.write(prompt)
        stream.flush()
    # NOTE: The Python C API calls flockfile() (and unlock) during readline.
    #line = inpu.readline()
    line = ''
    ch = ''
    while True:
        #ch = raw_inputch(inpu)
        fd = inpu.fileno()
        if inpu.isatty() and stream.isatty():
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        ch = inpu.read(1)
        if inpu.isatty() and stream.isatty():
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        chb = bytes(ch, 'ascii')
        if ch == '\b' or chb == b'\x7f':
            if len(line) > 0:
                line = line[:-1]
                stream.write('\b \b')
                stream.flush()
        elif ch in ('\n', '\r'):
            return line
        elif chb == b'\0':
            continue
        else:
            line = line + ch
            if echochar is not None:
                if len(echochar) > 0:
                    stream.write(echochar)
                    stream.flush()
            else:
                stream.write(ch)
                stream.flush()

def raw_inputch(inpu=sys.stdin):
    fd = inpu.fileno()
    if inpu.isatty():
        old_settings = termios.tcgetattr(fd)
    try:
        if inpu.isatty():
            tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        if inpu.isatty():
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

SSH_CONN_KEY = 'SSH_CONNECTION'
if len(sys.argv) == 2:
    local_ip_addr = sys.argv[1]
    remote_ip_addr, remote_port, local_ip_addr, local_port = local_ip_addr, 22, local_ip_addr, 22
else:
    try:
        ssh_conn = os.environ[SSH_CONN_KEY]
        ssh_conn_l = os.environ[SSH_CONN_KEY].split()
        if len(ssh_conn_l) != 4:
           raise Exception('Environment variable {} is not in the expected `address port address port\' format: {}'.format(SSH_CONN_KEY, ssh_conn))
        remote_ip_addr, remote_port, local_ip_addr, local_port = ssh_conn_l
    except KeyError:
        local_ip_addr = '127.0.0.1'
        remote_ip_addr, remote_port, local_ip_addr, local_port = local_ip_addr, 22, local_ip_addr, 22
local_user = getpass.getuser()
# If the username is root, check for a home directory that looks like /home or /Users.
if local_user == 'root':
    homedir = expanduser("~")
    m = re.match("^.*/(?:Users|home)/.*(?<=/)([^/]+)/?", homedir)
    if m:
        local_user = m.group(1)
enable_password = 'asapass'
local_ip_addr_addr = local_ip_addr
local_ip_addr = ipaddress.ip_address(local_ip_addr)
if isinstance(local_ip_addr, IPv6Address):
    if local_ip_addr == IPv6Address('::1'):
        local_ip_addr = IPv4Address('127.0.0.1')
    else:
        raise Exception('IPv6 is not supported other than for loopback addresses like `::1\'.')
    local_hostname = 'localhost'
else:
    local_hostname = socket.getfqdn(str(local_ip_addr))
    if local_hostname == str(local_ip_addr):
        raise Exception('Cannot resolve IP address `{}\' to a hostname.'.format(local_ip_addr))

def flush():
    try:
        sys.stdout.flush()
    except:
        pass

grps = re.search(r"site(\d+)", local_hostname)
if grps:
    siteid = int(grps.group(1))
else:
    siteid = 1
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
prefixlen['management'] = 23
offsets['mpi'] = '0.128.0.0'
offsets['mpe'] = '0.128.0.128'
wan_interface = IPv4Interface(str(local_ip_addr) + '/' + str(prefixlen['wan']))
ifaces['wan'] = wan_interface.network.with_netmask.replace('/', ' ')
peers['wan'] = ip_address(wan_interface.ip) + 1

wan_classa = IPv4Interface(str(local_ip_addr) + '/8').network.network_address
wan_classa_base = wan_classa + ((siteid - 1) * pow(2, 32 - prefixlen['wan']))
if wan_classa_base != wan_interface.network.network_address:
    print('''The incoming IP address does not appear to be a valid management address.
If you are using SSH to connect to the host that is running this program,
you may need to pass in a command line parameter of `127.0.0.1' to avoid
trying to use the host's default IP address as the mocked management address.
''', file=sys.stderr, end='')
    sys.exit(1)

bases = {}
bases['users'] = '10.100.0.0'
bases['management'] = '172.16.0.0'

interface_list = ['wan', 'mpe', 'mpi', 'users']

ntwks_base['wan'] = ip_address(str(wan_classa))
ntwks_base['mpi'] = ip_address(str(wan_classa + int(ip_address(offsets['mpi']))))
ntwks_base['mpe'] = ip_address(str(wan_classa + int(ip_address(offsets['mpe']))))
ntwks_base['users'] = ip_address(bases['users'])

for iface in ntwks_base:
    ntwks[iface] = ntwks_base[iface] + ((siteid - 1) * pow(2, 32 - prefixlen[iface] + prefixlen_noncontig[iface]))

ntwks['management'] = ip_address(bases['management'])

for iface in ntwks:
    ifaces[iface] = IPv4Interface(str(ntwks[iface] + 1) + '/' + str(prefixlen[iface])).with_netmask.replace('/', ' ')

ifaces['management'] = IPv4Interface(str(ntwks['management'] + siteid) + '/' + str(prefixlen['management'])).with_netmask.replace('/', ' ')

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
    'management_network': ntwks['management'],
    'management_address': ifaces['management'],
}

device = ASA(configstr=asa_config(**kwds), config='conf-{}.txt'.format(local_hostname))
    
transscriptf = open(local_hostname + '.transcript.log', "a+")
transscriptf2 = open('all.transcript.log', "a+")

def printt(s, end='\n', nostdout=False, transscriptf=transscriptf, transscriptf2=transscriptf2):
    files = [transscriptf, transscriptf2]
    if not nostdout:
        files.append(sys.stdout)
    s = s.split('\n')
    for ln in s[:-1]:
        for f in files:
            print((str(os.getpid()) + ' ' if f == transscriptf else '') + ln, file=f)
            f.flush()
    for f in files:
        print((str(os.getpid()) + ' ' if f == transscriptf else '') + s[-1], file=f)
        f.flush()
    for f in files:
        f.flush()
import sys

def syslog_msg(m, date="{:%b %d %Y %H:%M:%S}".format(datetime.now(timezone.utc)), logging_id=local_hostname, facility='local7', severity='notice', end='\n'):
    if facility == 'local7':
        facility = 23
    if severity == 'notice':
        severity = 5
    pri = facility * 8 + severity
    return '<{}>{} {} : {}{}'.format(pri, date, logging_id, m, end)

def syslog_msg_cmd(cmd, user=local_user):
    return "%ASA-5-111008: User '{}' executed the '{}' command.".format(user, cmd)

def send_syslog_msg(m, dest=remote_ip_addr, src=local_ip_addr_addr, port=514):
    m = m.encode('ascii')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((src, port))
    except PermissionError:
        sock.bind((src, 0))
    sock.sendto(m, (dest, port))

#send_syslog_msg(syslog_msg(syslog_msg_cmd('access-list josh extended permit ip any any')))

def fmt_banner(s, line_len=78, before='# ', after='#'):
    return '{}{}{}{}'.format(before, s, ' ' * (line_len - len(before) - len(s) - len(after)), after)

motd = '''\

##############################################################################
#                                                                            #
# A typical banner or legal notice goes here.                                #
#                                                                            #
''' + fmt_banner(local_hostname) + '''
#                                                                            #
''' + fmt_banner('You are: {}@{}'.format(local_user, remote_ip_addr)) + '''
#                                                                            #
##############################################################################
Type help or '?' for a list of available commands.

'''

printt(motd, end='')

in_enable = False

from getpass import getpass

pager_size = 24
width_size = 80

outp = ''
history = prompt_toolkit.history.InMemoryHistory()
vi_mode = False
prompt_mode = False
while not device.check_exit():
    if sys.stdout.isatty() and sys.stdin.isatty() and prompt_mode:
        try:
            ln = prompt_toolkit.shortcuts.prompt(device.get_prompt(), history=history, vi_mode=vi_mode);
        except EOFError:
            ln = 'logout'
    else:
        print(device.get_prompt(), end='')
        flush()
        ln = _raw_input()
        print()
        flush()
    printt(device.get_prompt() + ln, nostdout=True)
    ln = ln.rstrip()
    filt = None
    if ln == 'set -o vi':
        vi_mode = True
        prompt_mode = True
        continue
    elif ln == 'set -o emacs':
        vi_mode = False
        prompt_mode = True
        continue
    elif ln in ('en', 'ena', 'enab', 'enabl', 'enable'):
        enablepasswordln = asa_getpass()
        printt('Password: ' + '*' * len(enablepasswordln), nostdout=True)
        if '{}'.format(enable_password) != enablepasswordln:
            printt('Invalid password.')
        else:
            device.send('enable')
            in_enable = True
        continue
    filt = None
    if re.search(r" \| i(|nclude) ", ln) is not None:
        grps = re.match(r"^([^|]*) \| (?:i|include) (.*)$", ln)
        if grps:
            ln = grps.group(1)
            filt = grps.group(2)
    if re.search(r'^\s+terminal width (\d+)\s*$', ln):
        width_size = re.match(r'^\s+terminal width (\d+)\s*$', ln).groups(1)
        if width_size < 0:
            width_size = 0
    elif re.search(r'^\s+terminal pager (\d+)\s*$', ln):
        pager_size = re.match(r'^\s+terminal pager (\d+)\s*$', ln).groups(1)
        if pager_size < 0:
            pager_size = 0
    elif in_enable and ln == 'show clock':
        locale.setlocale(locale.LC_TIME, "C")
        outp += "{:%H:%M:%S.0 %Z %a %b %d %Y}".format(datetime.now(timezone.utc))
    elif in_enable and ln == 'show mem':
        outp += '''\
Free memory:        1441865728 bytes (67%)
Used memory:         705617920 bytes (33%)
-------------     ------------------
Total memory:       2147483648 bytes (100%)

Virtual platform memory
-----------------------
Provisioned       2048 MB
Allowed              0 MB
Status            Noncompliant: Over-provisioned
'''
    elif in_enable and ln in ('show cpu', 'sh cpu'):
        outp += '''\
CPU utilization for 5 seconds = 1%; 1 minute: 1%; 5 minutes: 0%

Virtual platform CPU resources
------------------------------
Number of vCPUs              :     1
Number of allowed vCPUs      :     0
vCPU Status                  :  Noncompliant: Over-provisioned
'''
    elif ln in ('show ver', 'show version', 'sh ver', 'sh version'):
        outp += '''\

Cisco Adaptive Security Appliance Software Version 9.5(2)204
Device Manager Version 7.5(2)

Compiled on Mon 15-Feb-16 19:00 PST by builders
System image file is "boot:/asa952-204-smp-k8.bin"
Config file at boot was "startup-config"

asav-1 up 15 days 22 hours

Hardware:   ASAv, 2048 MB RAM, CPU Pentium II 2000 MHz,
Model Id:   ASAv10
Internal ATA Compact Flash, 129024MB
Slot 1: ATA Compact Flash, 129024MB
BIOS Flash Firmware Hub @ 0x0, 0KB


 0: Ext: Management0/0       : address is fa16.3e06.211c, irq 11
 1: Ext: GigabitEthernet0/0  : address is fa16.3e5f.a0b3, irq 11
 2: Ext: GigabitEthernet0/1  : address is fa16.3ec9.0bdd, irq 10
 3: Ext: GigabitEthernet0/2  : address is fa16.3e9a.d57b, irq 10
 4: Ext: GigabitEthernet0/3  : address is fa16.3e01.0452, irq 11

License mode: Smart Licensing
ASAv Platform License State: Unlicensed
No active entitlement: no feature tier and no throughput level configured
*Memory resource allocation is more than the permitted limit.

Licensed features for this platform:
Maximum Physical Interfaces       : 10
Maximum VLANs                     : 50
Inside Hosts                      : Unlimited
Failover                          : Active/Standby
Encryption-DES                    : Enabled
Encryption-3DES-AES               : Enabled
Security Contexts                 : 0
Carrier                           : Disabled
AnyConnect Premium Peers          : 2
AnyConnect Essentials             : Disabled
Other VPN Peers                   : 250
Total VPN Peers                   : 250
AnyConnect for Mobile             : Disabled
AnyConnect for Cisco VPN Phone    : Disabled
Advanced Endpoint Assessment      : Disabled
Shared License                    : Disabled
Total UC Proxy Sessions           : 2
Botnet Traffic Filter             : Enabled
Cluster                           : Disabled

Serial Number: 9AJDFJGV165

Image type          : Release
Key version         : A

Configuration last modified by enable_15 at 19:38:37.284 UTC Thu Mar 30 2017
'''
    elif in_enable and ln == 'show ipv6 access-list':
        pass
    elif in_enable and re.match('^\s*$', ln):
        pass
    elif in_enable or ln in ('quit', 'logout', 'exit', 'ex', 'log', 'qu'):
        response = device.send(ln)
        if re.match(r'^\s*(obj|acc|wr)', ln):
            send_syslog_msg(syslog_msg(syslog_msg_cmd(ln.strip().replace("'", "\\'"))))
        if response == 1:
            break
        if response is not None:
            outp += response
    else:
        outp = device.return_invalid_input()
    if len(outp) > 0:
        if device.check_error() or (filt is None and pager_size == 0):
            printt(outp)
        else:
            outlines = 0
            ch = ''
            for l in outp.split('\n'):
                if filt is not None:
                    if filt in l:
                        outlines += 1
                        printt(l)
                else:
                    outlines += 1
                    printt(l)
                if pager_size > 0 and outlines >= pager_size:
                    print(MORE_STRING, end='')
                    flush()
                    ch = ''
                    while ch not in (' ', '\n', '\r', 'q'):
                        ch = raw_inputch()
                        if ch == ' ':
                            outlines = 0
                    print('\r' + ' ' * len(MORE_STRING) + '\r', end='')
                    flush()
                if ch == 'q':
                    break
        flush()
        outp = ''
printt('''\

Logoff

''',end='')
sys.exit(0)
