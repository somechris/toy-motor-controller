#!/usr/bin/python3
# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

import argparse
import logging

from bluepy import btle

import toy_motor_controller
from toy_motor_controller.bus.bluez import get_scanner
from toy_motor_controller.util import bytes_to_hex_string

LOG_FORMAT = ('%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] '
              '%(filename)s:%(lineno)d - %(message)s')
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def dump_uuid(uuid, args):
    ret = ''
    if args.mnemonics != 'replace':
        ret += f'uuid={uuid}'
    if args.mnemonics != 'hide':
        name = uuid.getCommonName()
        uuid_str = str(uuid)
        if name != uuid_str or args.mnemonics == 'replace':
            if ret:
                ret += ', '
            ret += f'name={name}'
    return ret


def dump_descriptor(descriptor, args):
    print('      Descriptor('
          f'handle={descriptor.handle}, '
          f'{dump_uuid(descriptor.uuid, args)})')


def dump_characteristic(characteristic, args):
    properties = [name
                  for (mask, name) in btle.Characteristic.propNames.items()
                  if ((characteristic.properties & mask) == mask)
                  ]
    print('    Characteristic('
          f'handle={characteristic.handle}, '
          f'val_handle={characteristic.valHandle}, '
          f'{dump_uuid(characteristic.uuid, args)}, '
          f'properties={properties})')
    if (args.dump_characteristic_readable_data or args.dump_all) \
            and characteristic.supportsRead():
        data = characteristic.read()
        try:
            print(f'        data (utf8): {data.decode()}')
        except UnicodeDecodeError:
            # data cannot get decoded to utf8. So we skip it.
            pass
        print(f'        data  (hex): {bytes_to_hex_string(data, " ")}')
        print(f'        data  (raw): {data}')
        print(f'        data  (len): {len(data)}')

    if args.dump_descriptors or args.dump_all:
        for descriptor in characteristic.getDescriptors():
            dump_descriptor(descriptor, args)


def dump_service(service, args):
    print(f'  Service({dump_uuid(service.uuid, args)}, '
          f'handle_start={service.hndStart}, '
          f'handle_end={service.hndEnd})')
    if args.dump_characteristics or args.dump_all:
        for characteristic in service.getCharacteristics():
            dump_characteristic(characteristic, args)


def dump_services(address, args):
    device = btle.Peripheral(address)
    for service in device.getServices():
        dump_service(service, args)
    device.disconnect()
    print('---')


def get_dumper(args):
    address = args.address
    min_rssi = args.min_rssi
    if address is not None:
        address = address.lower()

    def dumper(advertisement):
        if min_rssi is None or min_rssi <= advertisement.rssi:
            if address is None or address == advertisement.address.lower():
                if args.mnemonics == 'hide':
                    str_arg = 'replace'
                elif args.mnemonics == 'add':
                    str_arg = 'add'
                elif args.mnemonics == 'replace':
                    str_arg = None
                else:
                    raise RuntimeError('Logic error')
                print(advertisement.__str__(raw_data=str_arg))

                if args.dump_services or args.dump_all:
                    dump_services(advertisement.address, args)

    return dumper


def main(args):
    logger.debug('Starting toy-motor-controller')
    toy_motor_controller.start()

    logger.debug('Initializing scanner')
    scanner = get_scanner(active=args.active)
    dumper = get_dumper(args)

    logger.debug('Starting scanner')
    scanner.register(dumper)

    if not args.silent:
        print('Press the enter key to stop the scanner')
    input()

    logger.debug('Cleaning up')
    scanner.unregister(dumper)
    toy_motor_controller.stop()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Bluetooth Advertisement Dumper',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--verbose', '-v',
                        default=0,
                        action='count',
                        help='increase verbosity')

    parser.add_argument('--silent',
                        action='store_true',
                        help='dump only found advertisements')

    parser.add_argument(
        '--mnemonics',
        choices=['replace', 'add', 'hide'],
        default='replace',
        help='controls how to show mnemonics for numeric values. "replace" '
        'replaces numbers by their mnemonics if possible. "add" shows both '
        'numbers and mnemonics. "hide" hides mnemonics and shows only '
        'numbers')

    parser.add_argument('--min-rssi',
                        type=int, default=None,
                        help='Hide advertisements with rssi below this value')

    parser.add_argument('--active',
                        action='store_true',
                        help='perform active (instead of the default passive) '
                        'scans')

    parser.add_argument('--address',
                        default=None,
                        help='only show matches from this address')

    parser.add_argument(
        '--dump-services',
        action='store_true',
        help='try to dump service data. This will get the scanner stuck, if '
        'a device does not support service data extraction. Use "--address" '
        'to limit to a single device, to avoid getting stuck when another '
        'device\'s advertisement gets scanned before the target device.')

    parser.add_argument(
        '--dump-characteristics',
        action='store_true',
        help='Dump characteristi cs for each dumped service. This implies '
        '--dump-services.')

    parser.add_argument(
        '--dump-descriptors',
        action='store_true',
        help='Dump descriptors for each dumped characteristic. This implies '
        '--dump-characteristics')

    parser.add_argument(
        '--dump-characteristic-readable-data',
        action='store_true',
        help='Dumps the data that can be read from dumped characteristics. '
        'This implies --dump-characteristics')

    parser.add_argument(
        '--dump-all',
        action='store_true',
        help='Turns all --dump-* arguments on')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.silent:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dump_characteristic_readable_data:
        args.dump_characteristics = True

    if args.dump_descriptors:
        args.dump_characteristics = True

    if args.dump_characteristics:
        args.dump_services = True

    main(args)
