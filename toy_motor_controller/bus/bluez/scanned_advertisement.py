# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

class ScannedAdvertisement(object):
    def __init__(self, scanEntry):
        self._scanEntry = scanEntry

    @property
    def address(self):
        return self._scanEntry.addr

    @property
    def addressType(self):
        return self._scanEntry.addrType

    @property
    def connectable(self):
        return self._scanEntry.connectable

    @property
    def rssi(self):
        return self._scanEntry.rssi

    @property
    def rawData(self):
        ret = {}
        for (tagId, _, tagValue) in self._scanEntry.getScanData():
            ret[tagId] = tagValue
        return ret

    @property
    def data(self):
        ret = {}
        for (_, tagName, tagValue) in self._scanEntry.getScanData():
            ret[tagName] = tagValue
        return ret

    def __str__(self, rawData=False):
        data = f'rawData={self.rawData}' if rawData else f'data={self.data}'
        return f'{self.__class__.__name__}(address={self.address}, '\
            f'rssi={self.rssi}, connectable={self.connectable}, '\
            f'{data})'
