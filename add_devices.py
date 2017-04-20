#!/opt/tufin/securitysuite/ps/python/bin/python3.4

import argparse
import sys
import logging
import csv

sys.path.append("/opt/tufin/securitysuite/ps/lib")
from Secure_Common.Logging.Logger import setup_loggers, remove_logger_handlers
from Secure_Common.REST_Functions.Config import Secure_Config_Parser

from Secure_Common.Logging.Defines import COMMON_LOGGER_NAME

logger = logging.getLogger(COMMON_LOGGER_NAME)

class Device_Adder:

    headers = ['management_ip', 'management_name', 'management_type', 'log_associated_cma',
               'audit_log_source_id', 'cp_type', 'device_terminal_type', 'device_username',
               'device_password', 'device_enable_password', 'started', 'disabled', 'server_id',
               'is_offline', 'is_migrated', 'monitoring_use_defaults', 'customer_id',
               'monitoring_mode', 'port', 'dynamic_topology_data_mode', 'is_asbr', 'has_topology',
               'to_be_deleted', 'is_zone_based', 'fw1_regular_log_mode', 'object_usage_mode',
               'device_use_enable',
              ]

    def __init__(self, st_helper):
        self.st_helper = st_helper

    def add(self, ip_addr, devicetype, login={'username': 'user', 'password': 'pass'}, name=None, terminal_type='ssh', disabled=True, server_id=1):
        BLANK_STR = "''"
        HAS_ENABLE_PASSWORD = ['router', 'l3_switch', 'asa']
        USES_ENABLE_PASSWORD = ['router']
        TERMINAL_TYPES = ['ssh', 'telnet']

        if terminal_type not in TERMINAL_TYPES:
            raise Exception("Terminal type `{}' is not valid.".format(terminal_type))

        if name is None:
            name = '{}_{}'.format(ip_addr, devicetype)
#        logger.info("Adding a {} called {} on {} via {}".format(devicetype, name, ip_addr, terminal_type))
        d = dict()
        for i in self.headers:
            d[i] = BLANK_STR
        d['management_ip'] = ip_addr
        d['management_name'] = name
        d['management_type'] = 'Cisco'
        d['log_associated_cma'] = BLANK_STR
        d['audit_log_source_id'] = BLANK_STR
        d['cp_type'] = devicetype
        d['device_terminal_type'] = terminal_type
        d['device_username'] = login['username']
        d['device_password'] = login['password']
        d['device_enable_password'] = d['device_password'] if devicetype in HAS_ENABLE_PASSWORD else BLANK_STR
        d['started'] = 'f'
        d['disabled'] = 't' if disabled else 'f'
        d['server_id'] = str(server_id)
        d['is_offline'] = 'f'
        d['is_migrated'] = 'f'
        d['monitoring_use_defaults'] = 't'
        d['customer_id'] = '1'
        d['monitoring_mode'] = 'periodic'
        d['port'] = str(22 if terminal_type == 'ssh' else 23 if terminal_type == 'telnet' else None)
        d['dynamic_topology_data_mode'] = str(0)
        d['is_asbr'] = 'f'
        d['has_topology'] = 't'
        d['to_be_deleted'] = 'f'
        d['is_zone_based'] = str(0)
        d['fw1_regular_log_mode'] = str(0)
        d['object_usage_mode'] = str(0)
        d['device_use_enable'] = 't' if devicetype in USES_ENABLE_PASSWORD else BLANK_STR

        device_str = \
            d['management_ip'] + ',' + d['management_name'] + ',' + d['management_type'] + ',' + BLANK_STR + ',' + BLANK_STR + ',' + d['cp_type'] + ',' + d['device_terminal_type'] + ',' +\
            d['device_username'] + ',' + d['device_password'] + ',' + d['device_enable_password'] + ',' + d['started'] + ',' + d['disabled'] + ',' + d['server_id'] + ',' + d['is_offline'] + ',' +\
            d['is_migrated'] + ',' + d['monitoring_use_defaults'] + ',' + d['customer_id'] + ',' + d['monitoring_mode'] + ',' + d['port'] + ',' + d['dynamic_topology_data_mode'] + ',' +\
            d['is_asbr'] + ',' + d['has_topology'] + ',' + d['to_be_deleted'] + ',' + d['is_zone_based'] + ',' + d['fw1_regular_log_mode'] + ',' + d['object_usage_mode'] + ',' + \
            d['device_use_enable']

#       st_helper.post_device('{}\n{}'.format(headers, device_str))
        print(device_str)

    def printheader(self):
        print(format(','.join(self.headers)))

def process_cli_args(me, cli_args, conf):
    if cli_args.log_file:
        log_file = cli_args.log_file
    else:
        log_file = '{}.log'.format(me)
    log_levels = conf.dict('log_levels')
    if cli_args.log_level:
        for k in log_levels:
            log_levels[k] = cli_args.log_level.upper()
    elif cli_args.debug:
        for k in log_levels:
            log_levels[k] = 'DEBUG'
#    if sys.stdout.isatty and sys.stderr.isatty and sys.stdin.isatty:
#        if not cli_args.debug:
#            print("You have not specified --debug. All output will be going to the logfile in `{}{}'.".format(conf.get('common', 'log_file_path'), log_file))
#    setup_loggers(log_levels, log_to_stdout=cli_args.debug, log_file=log_file, no_format=True if cli_args.debug else False)

def get_cli_args():
    parser = argparse.ArgumentParser('add_devices')
    parser.add_argument('-i', '--device-management-ip-addr', required=True, help='Add a single device with the management IP address given.')
    parser.add_argument('-t', '--device-type', required=True, help="Specify the device type. Allowed values are `l3_switch', `nexus', `router'.")
    parser.add_argument('-n', '--device-management-name', help="Specify the device name. If not specified, defaults to the the `device_type_management_IP_addr'.")
    parser.add_argument('-f', '--input-file', help="Accept input from a CSV file. The first row must be a header line with column names of `manageent_ip_addr', `type', `management_name', and `terminal_type'.")
    parser.add_argument('-u', '--device-username', required=True, help="The username used to log in to the device.")
    parser.add_argument('-w', '--device-password', required=True, help="The password used to log in to the device.")
    parser.add_argument('-l', '--device-login', help="The name of the username and password login entry in the secure store for the device. Use set_secure_store.py -s <login> to add an entry.")
    parser.add_argument('-p', '--device-terminal-type', default='ssh', help="The connection method. Allowed values are `ssh' and `telnet'. The default is SSH.")
    parser.add_argument('--server-id', default=1, type=int, help='Specify the server ID for a remote collector.')
    parser.add_argument('-e', '--enabled', action='store_true', help='Create the device enabled. The default is to create it disabled.')
    parser.add_argument('-d', '--debug', action='store_true', help="Print out logging information to stdout in a concise format and set the default log level to `debug'.")
    parser.add_argument('--log-level', help="Set logging level to regardless of configured log levels. Levels are `error' (the default), `warn', `info', and 'debug'.")
    parser.add_argument('--log-file', help='Change the log file from the default.')
    args = parser.parse_args()
    return args

def main():
    me = 'add_devices'
    cli_args = get_cli_args()
    conf = Secure_Config_Parser()
    process_cli_args(me, cli_args, conf)
#    st_helper = Secure_Track_Helper.from_secure_config_parser(conf)
#    device_adder = Device_Adder(st_helper)
    device_adder = Device_Adder(None)

    if cli_args.device_login is not None:
        logger.error("Using --device-login is not supported yet.")
        return 1

    if cli_args.input_file is not None:
        logger.error("Using --input-file is not supported yet.")
        return 1

    if cli_args.enabled is True:
        logger.error("Using --enabled is not supported yet.")

    if cli_args.device_type not in ['l3_switch', 'nexus', 'router', 'asa']:
        logger.error("Unsupported device type `{}'.".format(cli_args.device_type))
        return 1

    if cli_args.device_management_name is None:
        name = '{}_{}'.format(cli_args.device_management_ip_addr, cli_args.device_type)
    else:
        name = cli_args.device_management_name

    device_adder.printheader()
    ip_addr = cli_args.device_management_ip_addr
    site_no = 1
    for ip_addr in sys.stdin:
        ip_addr = ip_addr.strip()
        management_name = 'asa214-site{}'.format(site_no)
        site_no += 1
        device_adder.add(ip_addr, cli_args.device_type,
                login={'username': cli_args.device_username, 'password': cli_args.device_password},
                name=management_name, terminal_type=cli_args.device_terminal_type,
                disabled=False if cli_args.enabled else True,
                server_id=cli_args.server_id,
                )

    return 0

if __name__ == '__main__':
    sys.exit(main())
