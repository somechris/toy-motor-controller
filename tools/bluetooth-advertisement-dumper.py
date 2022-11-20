#!/usr/bin/python3
# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

import argparse
import logging

import toy_motor_controller
from toy_motor_controller.bus.bluez import get_scanner

LOG_FORMAT = ('%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] '
              '%(filename)s:%(lineno)d - %(message)s')
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

def dumper(advertisement):
    print(advertisement)

def main(args):
    logger.debug('Starting toy-motor-controller')
    toy_motor_controller.start()

    logger.debug('Initializing scanner')
    scanner = get_scanner()

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

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    if args.silent:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)

    main(args)