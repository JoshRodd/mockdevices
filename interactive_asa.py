#!/usr/bin/env python3
"""
    Author: Nate Rodd
    Version: 0.1
    Description: Module with ASA class to  simulate interacting with a Cisco ASA. The below commands are supported.
        - enable
        - show running-config
        - show object-group (id <name>)?
        - show access-list (<acl name>)?
        - show ipv6 access-list (<acl name>)?
            - command is accepted, but will never get any output, regardless of config
        - end
        - exit
        - service, network, and icmp object-group creation
            - port-object, service-object and icmp object creation when at the correct config level
        - access-list creation with or without object-groups
        - no object-group <type> <name>
        - no access-list <details .*>

    ToDo:
        - add support for delete by object-group id
        - add unit tests for all methods
        - add delete object-group element functionality
        - re-factor code to be more compact and readable
        - add show clock command
        - add show version command
        - add context switching
"""
import re
from collections import defaultdict
import binascii
import sqlite3
import os
# import time
# from pprint import pprint


class ASA:
    object_group_re = re.compile(r'^\s*object-group (?P<type>\S+) (?P<name>\S+)')
    service_object_re = re.compile(r'^\s*service-object (?P<protocol>\S+) ?(((?P<type>(source|destination)) )?((?P<operator>\S+) (?P<svc>.+)$)?)?')
    port_object_re = re.compile(r'^\s*port-object (?P<object>.*)$')
    network_object_re = re.compile(r'^\s*network-object (?P<object>.*)')
    icmp_object_re = re.compile(r'^\s*icmp-object (?P<object>.*)')
    acl_re = re.compile(r'access-list '
                        r'(?P<name>\S+)( line '
                        r'(?P<line>\d+))?'
                        r'(?P<type> extended| remark'
                        r'(?P<remark>.*))?( '
                        r'(?P<action>permit|deny) '
                        r'(?P<protocol>\d{1,3}|object-group '
                        r'(?P<svc_group>\S+)|[a-z]+) '
                        r'(?P<src>'
                        r'(?P<src_network>([0-9]{1,3}\.){3}[0-9]{1,3} ([0-9]{1,3}\.){3}[0-9]{1,3})|host '
                        r'(?P<src_host>([0-9]{1,3}\.){3}[0-9]{1,3})|object-group '
                        r'(?P<src_group>\S+)|any\d?) '
                        r'(?P<dst>'
                        r'(?P<dst_network>([0-9]{1,3}\.){3}[0-9]{1,3} ([0-9]{1,3}\.){3}[0-9]{1,3})|host '
                        r'(?P<dst_host>([0-9]{1,3}\.){3}[0-9]{1,3})|object-group '
                        r'(?P<dst_group>\S+)|any\d?)( '
                        r'(?P<svc_type>(eq |gt |range |object-group )?'
                        r'(?P<svc>.+)$))?)?(\s*log default\s*)?$')

    def __init__(self, config=None, configstr=None, hits_db='asa.sqlite'):
        assert config or configstr
        self.config_file = config
        if configstr is None:
            with open(config, "r") as cfg:
                self.config = [l.strip() for l in list(cfg)]
        else:
            if self.config_file is not None:
                try:
                    with open(config, "r") as cfg:
                        self.config = [l.rstrip() for l in list(cfg)]
                except IOError:
                    self.config = configstr.split('\n')
            else:
                self.config = configstr.split('\n')

        self.config_string = ''.join([i.rstrip() + '\n' for i in self.config])
        self.hostname = next(l for l in self.config if 'hostname' in l).split(' ')[1].rstrip()
        self.prompt_level = []
        self.prompt_end = '> '
        self.in_error = False
        self.in_exit = False

        self.update_dicts(self.config)

        if os.path.isfile(hits_db):
            db_conn = sqlite3.connect(hits_db)
            self.db_cur = db_conn.cursor()
        else:
            self.db_cur = None

    def update_dicts(self, lines):
        self.bound_object_groups = set()

        self.object_groups = defaultdict(list)
        self.acls = defaultdict(list)
        self.object_group_types = dict()
        self.acl_names = []

        obj = 0
        object_group_name = ''
        for line in lines:
            object_group = self.object_group_re.search(line)
            if object_group:
                obj = True
                object_group_name = object_group.group('name')
                object_group_type = object_group.group('type')
                self.object_group_types[object_group_name] = object_group_type
                self.object_groups[object_group_name] = []
                continue
            elif obj:
                network_object = self.network_object_re.search(line)
                service_object = self.service_object_re.search(line)
                port_object = self.port_object_re.search(line)
                icmp_object = self.icmp_object_re.search(line)
                if service_object:
                    self.object_groups[object_group_name].append({n: service_object.group(n) for n in service_object.groupdict()})
                elif network_object:
                    self.object_groups[object_group_name].append({n: network_object.group(n) for n in network_object.groupdict()})
                elif port_object:
                    self.object_groups[object_group_name].append({n: port_object.group(n) for n in port_object.groupdict()})
                elif icmp_object:
                    self.object_groups[object_group_name].append({n: port_object.group(n) for n in port_object.groupdict()})
                else:
                    obj = False
            if not obj:
                acl = self.acl_re.search(line)
                if acl:
                    name = acl.group('name')
                    if name not in self.acl_names:
                        self.acl_names.append(name)
                    self.acls[name].append({n: acl.group(n) for n in acl.groupdict()})
                    self.acls[name][-1]['line'] = self.acls[name][-1]['line'] + 1 if self.acls[name][-1]['line'] else 1
                    self.acls[name][-1]['acl'] = line.strip()

                    groups = ['svc_group', 'src_group', 'dst_group']
                    svc = acl.groupdict()['svc_type']

                    if svc and 'object-group' in svc:
                        groups.append('svc')

                    for group in groups:
                        bound_obj = acl.groupdict()[group]
                        if bound_obj:
                            self.bound_object_groups.add(bound_obj)

    def update_config(self):
        self.config_string = ''.join([i.rstrip() + '\n' for i in self.config])

    def write_memory(self, cmd):
        if self.config_file is not None:
            with open(self.config_file, 'w') as cfg:
                cfg.write(''.join(self.config_string))
                return """\
Building configuration...
Cryptochecksum: e141b46b e03631fe 797913f9 bdabdff5

12647 bytes copied in 0.390 secs
[OK]"""
        else:
            return """\
Building configuration...
Cryptochecksum: e141b46b e03631fe 797913f9 bdabdff5

%Error copying system:/running-config (No Device)
Error executing command
[FAILED]"""

    def get_prompt(self):
        return '{}{}{}'.format(self.hostname, '({})'.format(self.prompt_level[-1]) if self.prompt_level else '', self.prompt_end)

    def return_invalid_input(self):
        self.in_error = True
        return (
            '{m:>{w}}\n'.format(m='^', w=len([i for i in self.get_prompt()]) + 1) +
            "ERROR: % Invalid input detected at \'^\' marker.\n"
        )

    def return_incomplete(self):
        self.in_error = True
        return 'ERROR: % Incomplete command'

    def enable(self, cmd):
        if self.prompt_end == '# ':
            return self.return_invalid_input()
        else:
            self.prompt_end = '# '

    def config_t(self, cmd):
        if self.prompt_end != '# ':
            return self.return_invalid_input()
        self.prompt_level = ['config']
        self.current_object_group = False

    def end(self, cmd):
        if self.prompt_level:
            self.prompt_level = []
        else:
            return self.return_invalid_input()

    def exit(self, cmd):
        if self.prompt_level:
            self.prompt_level.pop()
        else:
            self.in_exit = True

    def show_run(self, cmd):
        show_run_acl = re.search(r'show running-config access-(?P<type>list|group)( (?P<acl_section>\S+))?$', cmd)
        show_running_config = re.search(r'show running-config$', cmd)
        show_run_object_group = re.search(r'show running-config object-group( id (?P<object_group_section>\S+))?$', cmd)

        if show_run_acl:
            show_type = show_run_acl.groupdict()['type']
            if show_run_acl.groupdict()['acl_section']:
                acl_section = show_run_acl.groupdict()['acl_section']
                if acl_section not in self.acls:
                    return 'ERROR: access-list <{}> does not exist'.format(acl_section)
            else:
                acl_section = ''
            return '\n'.join([l for l in self.config_string.split('\n') if re.search(r'^access-{}\s*{}'.format(show_type, acl_section), l)])

        elif show_run_object_group:
            object_group_id = show_run_object_group.groupdict()['object_group_section'] or None
            return self.show_object_group('show object-group', object_group_id)

        elif show_running_config:
            return self.config_string.rstrip()
        else:
            return self.return_invalid_input()

    def show_object_group(self, cmd, group_id=None):
        section = False
        output = ''
        for line in self.config:
            if section and re.search(r'^\s+\S', line):
                output += line + '\n'
            elif re.search(r'^object-group ', line) and (re.search(r'{}'.format(group_id), line) if group_id else True):
                output += line + '\n'
                section = True
            elif section:
                break
        if section:
            return output.rstrip()
        elif group_id:
            return 'object-group {} does not exist'.format(group_id)

    def show_access_list(self, cmd, access_list=None):

        if access_list and access_list not in self.acls:
            self.in_error = True
            return 'ERROR: access-list <{}> does not exist\n'.format(access_list) if access_list else ''

        output = []

        output.append(''
                      'access-list cached ACL log flows: total 0, denied 0 (deny-flow-max 4096)\n'
                      '            alert-interval 300')

        for name in self.acl_names:
            aces = self.acls[name]
            if access_list and name != access_list:
                continue
            acl_output = []
            line = 1
            elem = 0
            for ace in aces:
                services = []
                sources = []
                destinations = []
                top_ace = ace['acl']
                if 'remark' in top_ace:
                    acl_output.append(re.sub(r'access-list (\S+)', r"access-list \1 line {}".format(line), top_ace.rstrip()))
                    line += 1
                    continue
                else:
                    ace_hash = asa_hash("{action}{protocol}{src}{dst}{svc_type}".format(**ace))
                    hitcnt = self.get_hitcnt(ace_hash) or 0
                    acl_output.append('{} (hitcnt={}) {}'.format(re.sub(r'access-list (\S+)', r'access-list \1 line {}'.format(line),
                                                                 top_ace.rstrip()), hitcnt, ace_hash))

                if 'object-group' not in ace['acl']:
                    elem += 1
                    line += 1
                    continue

                if ace['svc_group']:
                    for obj in self.object_groups[ace['svc_group']]:
                        services.append([obj['protocol'], ''])
                        if obj['svc']:
                            services[-1][1] = ' {} {}'.format(obj['operator'], obj['svc'])
                        elif obj['type']:
                            services[-1][1] = ' {}'.format(obj['type'])
                else:
                    services.append([ace['protocol'], ''])
                    if ace['svc_type']:
                        if 'object-group' in ace['svc_type']:
                            for obj in self.object_groups[ace['svc']]:
                                services[-1][1] = ' {}'.format(obj['object'])
                        else:
                            services[-1][1] = ' {}'.format(ace['svc_type'])

                if ace['src_group']:
                    for obj in self.object_groups[ace['src_group']]:
                        sources.append(obj['object'])
                else:
                    sources = [ace['src']]

                if ace['dst_group']:
                    for obj in self.object_groups[ace['dst_group']]:
                        destinations.append(obj['object'])
                else:
                    destinations = [ace['dst']]

                for service in services:
                    for source in sources:
                        for destination in destinations:
                            elem += 1
                            ace_hash = asa_hash("{action}{protocol}{src}{dst}{svc_type}".format(action=ace['action'],
                                                                                                protocol=service[0],
                                                                                                src=source, dst=destination,
                                                                                                svc_type=service[1]))
                            hitcnt = self.get_hitcnt(ace_hash) or 0
                            acl_output.append('  access-list {name} line {line} extended {action} {protocol} {source} {destination}{service} (hitcnt={hitcnt}) {ace_hash}'.
                                              format(name=name, line=line, action=ace['action'], protocol=service[0], source=source,
                                                     destination=destination, service=service[1], hitcnt=hitcnt, ace_hash=ace_hash))

                line += 1

            acl_output.insert(0, 'access-list {}; {} elements; name hash: '.format(name, elem))
            acl_output[0] = '{}{}'.format(acl_output[0], asa_hash(name))
            output.extend(acl_output)
        return '\n'.join(output)

    def show_ipv6_access_list(self, cmd, line):
        pass

    def no(self, command):
        if 'config' not in self.prompt_level:
            return self.return_invalid_input()
        new_config = self.config[:]
        self.prompt_level = ['config']
        self.current_object_group = False
        command = re.sub(r'line \d+ ', '', command.rstrip())
        section = False

        obj_match = self.object_group_re.search(command.replace('no ', ''))
        obj_id_match = re.search(r'no object-group id (\S+)', command)
        acl_match = self.acl_re.search(command.replace('no', ''))
        acl_line_match = re.search(r'no access-list (?P<name>\S+) line (?P<number>\d+)', command)

        if obj_match:
            if obj_match.group('name') in self.bound_object_groups:
                return 'Removing object-group ({}) not allowed, it is being used.'.format(obj_match.group('name'))
        if obj_id_match:
            if obj_match.group('name') in self.object_groups:
                command = 'object-group {service} {name}'.format(service=self.object_groups(obj_match('name')), name=obj_match('name'))
            else:
                return 'Removing object-group ({}) failed; it does not exist'.format(obj_match.group('name'))
            if obj_id_match.group('name') in self.bound_object_groups:
                return 'Removing object-group ({}) not allowed, it is being used.'.format(obj_match.group('name'))

        line_num = 1
        for index, line in enumerate(self.config):
            if acl_line_match:
                if line_num == int(acl_line_match.group('number')):
                    new_config.pop(index)
                    section = True
                    break
                if acl_line_match.group('name') in line:
                    line_num += 1

            if command.replace('no ', '').strip() in line.strip():
                remove = index
                new_config.pop(remove)
                section = True
                continue
            elif section and re.search(r'^\s+\S', line):
                new_config.pop(remove)
                continue

            elif section:
                break
        if section:
            self.prompt_level = ['config']
            self.config = new_config[:]
            self.update_config()
            self.update_dicts(self.config)
        else:
            if obj_match:
                return 'Removing object-group ({}) failed; it does not exist'.format(obj_match.group('name'))
                # above case only technically handles object-groups that don't exist,
                # should be below if the object-group is configured in an ACl
                # return 'Removing object-group (<id>) not allowed, it is being used.'
            elif acl_match:
                if acl_match.group('name') in self.acls:
                    self.in_error = True
                    return 'Specified access-list does not exist'
                else:
                    self.in_error = True
                    return 'ERROR: access-list <{}> does not exist'.format(acl_match.group('name'))
            else:
                return self.return_invalid_input()

    def object_group(self, line):
        o = self.object_group_re.search(line)

        if not o or not self.prompt_level or (self.prompt_level and self.prompt_level[0] != 'config'):
            return self.return_invalid_input()

        if o:
            if o.group('name') in self.object_groups and self.object_group_types[o.group('name')] != o.group('type'):
                return 'An object-group with the same id but different type (service) exists\n'
            elif o.group('type') == 'icmp':
                self.prompt_level = ['config', 'config-icmp-object-group']
            elif o.group('type') == 'service':
                self.prompt_level = ['config', 'config-service-object-group']
            elif o.group('type') == 'network':
                self.prompt_level = ['config', 'config-network-object-group']
            self.current_object_group = o.group('name')
            if o.group('name') not in self.object_groups:
                new_config = self.config[:]
                obj = False
                for n, l in enumerate(self.config):
                    if re.search(r'^object-group', l):
                        obj = True
                    if obj and not re.search(r'^(object-group| )', l):
                        new_config.insert(n, line)
                        self.current_line = n + 1
                        break
                self.config = new_config[:]
                self.update_config()
                self.update_dicts(self.config)
            else:
                self.current_line = next((i for i, j in enumerate(self.config) if line.strip() in j)) + 1
        else:
            return self.return_invalid_input()

    def object_group_element(self, line):
        new_config = self.config[:]
        p = self.port_object_re.search(line)
        n = self.network_object_re.search(line)
        i = self.icmp_object_re.search(line)
        s = self.service_object_re.search(line)
        if p and self.current_object_group and 'service' in self.prompt_level[-1]:
            if {j: p.group(j) for j in p.groupdict()} in self.object_groups[self.current_object_group]:
                return 'Adding obj ({} ) to grp ({}) failed; object already exists'.format(line.rstrip(), self.current_object_group)
        elif n and self.current_object_group and 'network' in self.prompt_level[-1]:
            if {j: n.group(j) for j in n.groupdict()} in self.object_groups[self.current_object_group]:
                return 'Adding obj ({} ) to grp ({}) failed; object already exists'.format(line.rstrip(), self.current_object_group)
        elif i and self.current_object_group and 'icmp' in self.prompt_level[-1]:
            if {j: i.group(j) for j in i.groupdict()} in self.object_groups[self.current_object_group]:
                return 'Adding obj ({} ) to grp ({}) failed; object already exists'.format(line.rstrip(), self.current_object_group)
        elif s and self.current_object_group and 'service' in self.prompt_level[-1]:
            if {j: s.group(j) for j in s.groupdict()} in self.object_groups[self.current_object_group]:
                return 'Adding obj ({} ) to grp ({}) failed; object already exists'.format(line.rstrip(), self.current_object_group)
        else:
            return self.return_invalid_input()

        new_config.insert(self.current_line, ' {}'.format(line.strip()))
        self.current_line += 1
        self.config = new_config[:]
        self.update_config()
        self.update_dicts(self.config)

    def access_list(self, line):
        if 'config' not in self.prompt_level:
            return self.return_invalid_input()

        new_config = self.config[:]
        section = False
        asection = False
        a = self.acl_re.search((line))

        if not a:
            return self.return_invalid_input()
        self.prompt_level = ['config']

        groups = ['svc_group', 'src_group', 'dst_group']
        svc = a.groupdict()['svc_type']

        if svc and 'object-group' in svc:
            groups.append('svc')
        for group in groups:
            obj = a.groupdict()[group]
            if obj:
                if obj not in self.object_groups:
                    self.in_error = True
                    return 'ERROR: specified object group <{}> not found'.format(obj)
                if group == 'svc_group' and self.object_group_types[obj] != 'service':
                    return 'ERROR: specified object group <{}> has wrong type; expecting service type'.format(obj)
                if group in ('dst_group', 'src_group') and self.object_group_types[obj] != 'network':
                    return 'ERROR: specified object group <{}> has wrong type; expecting network type'.format(obj)
                if not self.object_groups[obj]:
                    self.in_error = True
                    return 'ERROR: specified object group <{}> is empty'.format(obj)

        if re.sub(r' line \d+', '', line) not in (i['acl'] for i in self.acls[a.group('name')] if a.group('name') in self.acls):
            line_num = 1
            for n, l in enumerate(self.config):
                if re.search(r'^access-list', l):
                    asection = True
                if asection and a.group('name') in l:
                    section = True
                if a.groupdict()['line']:
                    if line_num == int(a.group('line')) and section:
                        new_config.insert(n, re.sub(r' line \d+', '', line))
                        break
                    if section:
                        line_num += 1
                if section and a.group('name') not in l:
                    new_config.insert(n, re.sub(r' line \d+', '', line))
                    break
                if asection and not re.search(r'^access-list', l):
                    new_config.insert(n, re.sub(r' line \d+', '', line))
                    break
        else:
            return 'WARNING: <{}> found duplicate element'.format(a.group('name'))

        self.prompt_level = ['config']

        self.current_object_group = False
        self.config = new_config[:]
        self.update_config()
        self.update_dicts(self.config)

    replacements = (
        ('', r'"'),
        ('log default', r'log Default'),
        ('show', r'^\s*sh(ow|o)?'),
        ('running-config', r'run(ning-config|ning-confi|ning-conf|ning-con|ning-co|ning-c|ning-|ning|nin|ni|n)?'),
        ('object-group', r'object-g(roup|rou|ro|r)?'),
        ('configure terminal', r'^\s*conf(ig|i)? t(erminal|ermina|ermin|ermi|erm|er|e)?'),
        ('enable', r'^\s*en(?=[^d])(able|abl|ab|a)?'),
        ('access-list', r'access-l(ist|is|i)?'),
        ('access-group', r'access-g(roup|rou|ro|r)?'),
        ('write memory', r'^\s*wr(ite|it|i)?\s+m(emory|emor|emo|em|e)?'),
    )

    commands = (
        (r'show\s+access-list\s*(?P<access_list>\S+)?\s*$', show_access_list),
        (r'show\s+ipv6\s+access-list.*$', show_ipv6_access_list),
        (r'show\s+object-group\s*(id\s+(?P<group_id>\S+))?\s*$', show_object_group),
        (r'show\s+running-config.*$', show_run),
        (r'^\s*end', end),
        (r'enable', enable),
        (r'configure\s+terminal', config_t),
        (r'^\s*(ex|exit|logout|q|quit)', exit),
        (r'^\s*no', no),
        (r'^\s*access-list', access_list),
        (r'^\s*object-group', object_group),
        (r'\s*(port-|service-|icmp-|network-)', object_group_element),
        (r'write memory', write_memory),
    )

    def send(self, command):
        for (replace, pattern) in self.replacements:
            command = re.sub(pattern, replace, command)

        valid = False
        for k, c in self.commands:
            m = re.search(k, command)
            if m:
                func = c
                args = m.groupdict()
                valid = True
                return func(self, command.strip(), **args)
        if not valid:
            return self.return_invalid_input()

    def check_error(self):
        if self.in_error:
            self.in_error = False
            return True
        return False

    def check_exit(self):
        return self.in_exit

    def get_hitcnt(self, ace_hash):
        if not self.db_cur:
            return None
        else:
            print(self.hostname, ace_hash)
            hits = self.db_cur.execute("SELECT cnt FROM hits WHERE name=? AND hash=?", (self.hostname, ace_hash,)).fetchone()
            return hits[0] if hits else None


def asa_hash(ace):
    print(ace)
    return str(hex(binascii.crc32(ace.encode())))
    # return '0x{:02x}'.format(hash(ace) % pow(2, 32))
