#!/usr/bin/env python3
import re
from collections import defaultdict
# import pprint

CONFIG_STRING = ''
OBJECT_GROUPS = defaultdict(list)
ACLS = defaultdict(list)
OUTPUT = []


def asa_hash(ace):
    return '0x{:02x}'.format(hash(ace) % pow(2, 32))


with open('asa.conf') as f:
    config = f.readlines()
    CONFIG_STRING = ''.join(config)
    object_group_re = re.compile('^object-group (?P<type>\S+) (?P<name>\S+)')
    service_object_re = re.compile('\s+service-object (?P<protocol>\S+) ?((?P<type>\S+) ?((?P<operator>\S+) (?P<svc>.+)$)?)?')
    port_object_re = re.compile('\s+port-object (?P<object>.*)$')
    network_object_re = re.compile('\s+network-object (?P<object>.*)')
    acl_re = re.compile('access-list '
                        '(?P<acl>\S+) '
                        '(?P<type>extended|remark '
                        '(?P<remark>.*))( '
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
    obj = 0
    object_group_name = ''
    for line in config:
        object_group = object_group_re.search(line)
        if object_group:
            obj = True
            object_group_name = object_group.group('name')
            continue
        elif obj:
            network_object = network_object_re.search(line)
            service_object = service_object_re.search(line)
            port_object = port_object_re.search(line)
            if network_object:
                OBJECT_GROUPS[object_group_name].append({n: network_object.group(n) for n in network_object.groupdict()})
            elif service_object:
                OBJECT_GROUPS[object_group_name].append({n: service_object.group(n) for n in service_object.groupdict()})
            elif port_object:
                OBJECT_GROUPS[object_group_name].append({n: port_object.group(n) for n in port_object.groupdict()})
            else:
                obj = False
        if not obj:
            acl = acl_re.search(line)
            if acl:
                name = acl.group('acl')
                ACLS[name].append({n: acl.group(n) for n in acl.groupdict()})
                ACLS[name][-1]['acl'] = line
OUTPUT.append('\
access-list cached ACL log flows: total 0, denied 0 (deny-flow-max 4096)\n\
            alert-interval 300')

for name, aces in ACLS.items():
    output = []
    line = 1
    elem = 0
    for ace in aces:
        services = []
        sources = []
        destinations = []
        top_ace = ace['acl']
        if 'remark' in top_ace:
            output.append(re.sub(r'access-list (\S+)', r"access-list \1 line {}".format(line), top_ace.rstrip()))
            line += 1
            continue
        else:
            output.append('{} (hitcnt=0) {}'.format(re.sub(r'access-list (\S+)', r'access-list \1 line {}'.format(line),
                                                           top_ace.rstrip()), asa_hash(top_ace)))

        if 'object-group' not in ace['acl']:
            elem += 1
            line += 1
            continue

        if ace['svc_group']:
            for obj in OBJECT_GROUPS[ace['svc_group']]:
                services.append([obj['protocol'], ''])
                if obj['svc']:
                    services[-1][1] = ' {} {}'.format(obj['operator'], obj['svc'])
                elif obj['type']:
                    services[-1][1] = ' {}'.format(obj['type'])
        else:
            services.append([ace['protocol'], ''])
            if ace['svc_type']:
                if 'object-group' in ace['svc_type']:
                    for obj in OBJECT_GROUPS[ace['svc']]:
                        services[-1][1] = ' {}'.format(obj['object'])

                else:
                    services[-1][1] = [' {}{}'.format(ace['svc_type'], ace['svc'])]

        if ace['src_group']:
            for obj in OBJECT_GROUPS[ace['src_group']]:
                sources.append(obj['object'])
        else:
            sources = [ace['src']]

        if ace['dst_group']:
            for obj in OBJECT_GROUPS[ace['dst_group']]:
                destinations.append(obj['object'])
        else:
            destinations = [ace['dst']]

        for service in services:
            for source in sources:
                for destination in destinations:
                    elem += 1
                    output.append('  access-list {name} line {line} extended {action} {protocol} {source} {destination}{service}'
                                  .format(name=name, line=line, action=ace['action'], protocol=service[0], source=source, destination=destination,
                                          service=service[1]))
                    output[-1] = '{} (hitcnt=0) {}'.format(output[-1], asa_hash(output[-1]))

        line += 1

    output.insert(0, 'access-list {}; {} elements; name hash: '.format(name, elem))
    output[0] = '{}{}'.format(output[0], asa_hash(output[-1]))
    OUTPUT.extend(output)

print('\n'.join(OUTPUT))
