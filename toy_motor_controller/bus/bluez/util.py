# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

from toy_motor_controller.util import normalize_mac_address
from toy_motor_controller.util import dict_get_int_or_None
from toy_motor_controller.util import dict_get_str_or_None


def convert_device_object_path_to_mac_address(object_path):
    if object_path is None:
        return None

    return normalize_mac_address(object_path[-17:].replace('_', ':'))


def normalize_io_options(options):
    return {
        'address': convert_device_object_path_to_mac_address(
            dict_get_str_or_None(options, 'device')),
        'offset': dict_get_int_or_None(options, 'offset'),
        'link': dict_get_str_or_None(options, 'link'),
        'mtu': dict_get_int_or_None(options, 'mtu'),
        'type_': dict_get_str_or_None(options, 'type'),
        }