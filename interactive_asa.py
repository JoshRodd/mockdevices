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
        - add check to ensure aces can't be added with non-existent object-groups
        - add check to ensure in-use object-groups can't be deleted
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
# import pprint


class ASA:
    object_group_re = re.compile('^object-group (?P<type>\S+) (?P<name>\S+)')
    service_object_re = re.compile('\s+service-object (?P<protocol>\S+) ?((?P<type>\S+) ?((?P<operator>\S+) (?P<svc>.+)$)?)?')
    port_object_re = re.compile('\s+port-object (?P<object>.*)$')
    network_object_re = re.compile('\s+network-object (?P<object>.*)')
    icmp_object_re = re.compile('\s+icmp-object (?P<object>.*)')
    acl_re = re.compile('access-list '
                        '(?P<name>\S+) '
                        '(?P<type>extended|remark '
                        '(?P<remark>.*))( line '
                        '(?P<line>\d+))?( '
                        '(?P<action>permit|deny) '
                        '(?P<protocol>\d{1,3}|object-group '
                        '(?P<svc_group>\S+)|[a-z]+) '
                        '(?P<src>(<?P<src_network>([0-9]{1,3}\.){3}[0-9]{1,3} ([0-9]{1,3}\.){3}[0-9]{1,3})|host '
                        '(?P<src_host>([0-9]{1,3}\.){3}[0-9]{1,3})|object-group '
                        '(?P<src_group>\S+)|any?) '
                        '(?P<dst>(?P<dst_network>([0-9]{1,3}\.){3}[0-9]{1,3} '
                        '([0-9]{1,3}\.){3}[0-9]{1,3})|host '
                        '(?P<dst_host>([0-9]{1,3}\.){3}[0-9]{1,3})|object-group '
                        '(?P<dst_group>\S+)|any?)( '
                        '(?P<svc_type>(eq |gt |range |object-group )'
                        '(?P<svc>.+)$))?)?')

    def __init__(self, config=None):
        self.config_file = config
        with open(config, "r+") as cfg:
            self.config = list(cfg)
        self.config_string = ''.join(self.config)
        self.hostname = next(l for l in self.config if 'hostname' in l).split(' ')[1].rstrip()
        self.prompt_level = []
        self.prompt_end = '> '

        self.object_groups = defaultdict(list)
        self.acls = defaultdict(list)
        self.update_dicts(self.config)

    def update_dicts(self, lines):

        obj = 0
        object_group_name = ''
        for line in lines:
            object_group = self.object_group_re.search(line)
            if object_group:
                obj = True
                object_group_name = object_group.group('name')
                object_group_type = object_group.group('type')
                self.object_groups[object_group_type] = object_group_type
                self.object_groups[object_group_name] = []
                continue
            elif obj:
                network_object = self.network_object_re.search(line)
                service_object = self.service_object_re.search(line)
                port_object = self.port_object_re.search(line)
                if network_object:
                    self.object_groups[object_group_name].append({n: network_object.group(n) for n in network_object.groupdict()})
                elif service_object:
                    self.object_groups[object_group_name].append({n: service_object.group(n) for n in service_object.groupdict()})
                elif port_object:
                    self.object_groups[object_group_name].append({n: port_object.group(n) for n in port_object.groupdict()})
                else:
                    obj = False
            if not obj:
                acl = self.acl_re.search(line)
                if acl:
                    name = acl.group('name')
                    self.acls[name].append({n: acl.group(n) for n in acl.groupdict()})
                    self.acls[name][-1]['line'] = self.acls[name][-1]['line'] + 1 if self.acls[name][-1]['line'] else 1
                    self.acls[name][-1]['acl'] = line

    def update_config_file(self):
        with open(self.config_file, 'w') as cfg:
            cfg.write(''.join(self.config))

    def get_prompt(self):
        return '{}{}{}'.format(self.hostname, '({})'.format(self.prompt_level[-1]) if self.prompt_level else '', self.prompt_end)

    def return_invalid_input(self):
        return (
            '{m:>{w}}\n'.format(m='^', w=len([i for i in self.get_prompt()])+1) +
            "ERROR: % Invalid input detected at \'^\' marker.\n"
        )

    def return_incomplete(self):
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
        if self.prompt:
            self.prompt.pop()
        else:
            return 1

    def show_run(self, cmd):
        return self.config_string

    def show_object_group(self, cmd, group_id=None):
        section = False
        output = ''
        for line in self.config:
            if section and re.search('^\s+\S', line):
                output += line
            elif re.search('^object-group ', line) and (re.search(' {}\s'.format(group_id), line) if group_id else True):
                output += line
                section = True
            elif section:
                break
        if section:
            return output.rstrip()
        elif group_id:
            return 'object-group {} does not exist'.format(group_id)

    def show_access_list(self, cmd, access_list=None):

        if access_list and access_list not in self.acls:
            return 'ERROR: access-list <{}> does not exist\n'.format(access_list) if access_list else ''

        output = []

        output.append(''
                      'access-list cached ACL log flows: total 0, denied 0 (deny-flow-max 4096)\n'
                      '            alert-interval 300')

        for name, aces in self.acls.items():
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
                    acl_output.append('{} (hitcnt=0) {}'.format(re.sub(r'access-list (\S+)', r'access-list \1 line {}'.format(line),
                                                                       top_ace.rstrip()), asa_hash(top_ace)))

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
                            services[-1][1] = [' {}{}'.format(ace['svc_type'], ace['svc'])]

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
                            acl_output.append('  access-list {name} line {line} extended {action} {protocol} {source} {destination}{service}'
                                              .format(name=name, line=line, action=ace['action'], protocol=service[0], source=source,
                                                      destination=destination, service=service[1]))
                            acl_output[-1] = '{} (hitcnt=0) {}'.format(acl_output[-1], asa_hash(acl_output[-1]))

                line += 1

            acl_output.insert(0, 'access-list {}; {} elements; name hash: '.format(name, elem))
            acl_output[0] = '{}{}'.format(acl_output[0], asa_hash(acl_output[-1]))
            output.extend(acl_output)
        return '\n'.join(output)

    def show_ipv6_access_list(self, cmd, line):
        pass

    def no(self, command):
        new_config = self.config
        self.prompt_level = ['config']
        self.current_object_group = False
        command = re.sub('line \d+ ', '', command.rstrip())
        section = False
        for line in self.config:
            if section and re.search('^\s+\S', line):
                new_config.remove(line)
            elif command.replace('no ', '').strip() == line.strip():
                new_config.remove(line)
                section = True
            elif section:
                break
        if section:
            self.config = new_config
            self.update_config_file()
            self.update_dicts(self.config)
        else:
            if 'object-group' in command:
                o = re.search('object-group \S+ (\S+)', command).group(1)
                return 'Removing object-group ({}) failed; it does not exist'.format(o)
                # above case only technically handles object-groups that don't exist,
                # should be below if the object-group is configured in an ACl
                # return 'Removing object-group (<id>) not allowed, it is being used.'
            elif 'access-list' in command:
                return 'Specified access-list does not exist'
                # above case only technically handles aces that don't exist,
                # should be below if the acl doesn't exist period
                # return 'ERROR: access-list <<acl>> does not exist'
            else:
                return self.return_invalid_input()

    def object_group(self, line):
        o = self.object_group_re.search(line)

        if not o or not self.prompt_level or (self.prompt_level and self.prompt_level[0] != 'config'):
            return self.return_invalid_input()

        if o:
            if o.group('name') in self.object_groups and self.object_groups[o.group('type')] != o.group('type'):
                return 'An object-group with the same id but different type (service) exists\n'
            elif o.group('type') == 'icmp':
                self.prompt_level = [self.prompt_level[0], 'config-icmp-object-group']
            elif o.group('type') == 'service':
                self.prompt_level = [self.prompt_level[0], 'config-service-object-group']
            elif o.group('type') == 'network':
                self.prompt_level = [self.prompt_level[0], 'config-network-object-group']
            self.current_object_group = o.group('name')
            if o.group('name') not in self.object_groups:
                new_config = self.config
                obj = False
                for n, l in enumerate(self.config):
                    if re.search('^object-group', l):
                        obj = True
                    if obj and not re.search('^(object-group| )', l):
                        new_config.insert(n, line)
                        self.current_line = n + 1
                        break
                self.config = new_config
                self.update_config_file()
                self.update_dicts(self.config)
            else:
                self.current_line = next((i for i, j in enumerate(self.config) if line in j)) + 1
        else:
            return self.return_invalid_input()

    def object_group_element(self, line):
        new_config = self.config
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
            if {j: s.group(j) for j in s.groupdict()} in self.bject_groups[self.current_object_group]:
                return 'Adding obj ({} ) to grp ({}) failed; object already exists'.format(line.rstrip(), self.current_object_group)
        else:
            return self.return_invalid_input()

        new_config.insert(self.current_line, line)
        self.current_line += 1
        self.config = new_config
        self.update_config_file()
        self.update_dicts(self.config)

    def access_list(self, line):
        new_config = self.config
        section = False
        asection = False
        a = self.acl_re.search((line))
        if not a:
            return self.return_invalid_input()

        if re.sub(' line \d+', '', line) not in (i['acl'] for i in self.acls[a.group('name')] if a.group('name') in self.acls):
            n = 0
            for n, l in enumerate(self.config):
                if a.groupdict()['line']:
                    if a.group('name') in l:
                        n += 1
                    if n == a.group('line'):
                        new_config.insert(n, line)
                        break
                if re.search('^access-list', l):
                    asection = True
                if a.group('name') in l:
                    section = True
                if section and a.group('name') not in l:
                    new_config.insert(n, re.sub(' line \d+', '', line))
                    break
                if asection and not re.search('^access-list', l):
                    new_config.insert(n, re.sub(' line \d+', '', line))
                    break
        else:
            return 'WARNING: <{}> found duplicate element'.format(a.group('name'))

        self.current_object_group = False
        self.config = new_config
        self.update_config_file()
        self.update_dicts(self.config)

    commands = [
        (r'^\s*sho?w? access-li?s?t?\S*( (?P<access_list>\S+)?)', show_access_list),
        (r'^\s*sho?w? ipv6? a', show_ipv6_access_list),
        (r'^\s*sho?w? object-g?r?o?u?p?\S*( (?P<group_id>\S+)?)', show_object_group),
        (r'^\s*sho?w? runi?n?g?-?c?o?n?f?i?g?', show_run),
        (r'^\s*end', end),
        (r'^\s*ena?b?l?e?', enable),
        (r'^\s*confi?g? te?r?m?i?n?a?l?', config_t),
        (r'^\s*exit', exit),
        (r'^\s*no', no),
        (r'^\s*access-l', access_list),
        (r'^\s*object-', object_group),
        (r'\s*(port-|service-|icmp-|network-)', object_group_element),
    ]

    def send(self, command):
        valid = False
        for k, c in self.commands:
            m = re.match(k, command)
            if m:
                func = c
                args = m.groupdict()
                valid = True
                return func(self, command, **args)
        if not valid:
            print(command)
            return self.return_invalid_input()


def asa_hash(ace):
    return '0x{:02x}'.format(hash(ace) % pow(2, 32))
