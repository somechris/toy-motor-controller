# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

import pprint

import dbus.service
import toy_motor_controller.bus.dbus

from toy_motor_controller.bus.dbus import PropertiesObject

from . import get_advertisement_manager
from . import LE_ADVERTISEMENT_IFACE
from . import Registree

import logging
logger = logging.getLogger(__name__)


class Advertisement(Registree, PropertiesObject):
    def __init__(self, **kwargs):
        super().__init__(
            manager=get_advertisement_manager(),
            main_interface=LE_ADVERTISEMENT_IFACE,
            **kwargs)

        self._local_name = None
        self._manufacturer_data = None
        self._data = None

    def advertise(self):
        self.register()

    def unadvertise(self):
        self.unregister()

    def _set_manufacturer_data(self, data):
        self._manufacturer_data = dbus.Dictionary({}, signature='qv')
        if data and len(data) >= 2:
            company_id = (data[1] << 8) + data[0]
            company_data = dbus.Array(data[2:], signature='y')
            self._manufacturer_data[company_id] = company_data

        self.update()

    def _set_local_name(self, local_name):
        self._local_name = local_name

        self.update()

    def _set_data(self, type_, value):
        if self._data is None:
            self._data = {}
        self._data[type_] = dbus.Array(value, signature='y')

        self.update()

    def _get_main_interface_properties(self):
        properties = {
            'Type': dbus.String('peripheral'),
            'MinInterval': dbus.UInt32(50),
            'MaxInterval': dbus.UInt32(150),
            }

        if self._local_name is not None:
            properties['LocalName'] = dbus.String(self._local_name)

        if self._manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self._manufacturer_data, signature='qv')

        if self._data is not None:
            properties['Data'] = dbus.Dictionary({}, signature='yv')
            for key, value in self._data.items():
                properties['Data'][key] = dbus.Array(value, signature='y')

        logger.debug('Properties of Advertisement:\n'
                     f'{pprint.pformat(properties)}')

        return properties

    @dbus.service.method(toy_motor_controller.bus.dbus.OM_IFACE,
                         in_signature='',
                         out_signature='a{sv}')
    def GetManagedObjects(self):
        return dbus.Dictionary({}, signature='sv')

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        pass
