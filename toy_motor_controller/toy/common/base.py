# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

import time


class DiscoveryBase(object):
    # -- Initialization ------------------------------------------------------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._connected = False

    # -- Scanning ------------------------------------------------------------

    def _start_scan(self, matches_map):
        raise NotImplementedError()

    def _stop_scan(self, scan_state):
        raise NotImplementedError()

    def scan(self, first=False, best=False, duration=10,
             strip_supplement=True):
        matches_map = {}
        stop_time = (time.time() + duration) if duration is not None else 0

        scan_state = self._start_scan(matches_map)

        while not (first and matches_map) and \
                (not stop_time or time.time() < stop_time):
            time.sleep(0.1)

        self._stop_scan(scan_state)

        matches = list(matches_map.values())
        matches.sort(key=lambda x: x.get('supplement', {}).get('key', 0))
        if strip_supplement:
            for match in matches:
                try:
                    del match['supplement']
                except KeyError:
                    # match did not have a supplement.
                    # So there is nothing to remove
                    pass

        if first or best:
            if matches:
                ret = matches[0]
            else:
                ret = None
        else:
            ret = matches

        return ret

    # -- Connecting ----------------------------------------------------------

    def connectFirst(self, duration=10):
        scan_result = self.scan(first=True, duration=duration)
        if scan_result is None:
            raise RuntimeError('Failed to find connectable device')
        return self.connect(**scan_result)

    def connectBest(self, duration=10):
        scan_result = self.scan(best=True, duration=duration)
        if scan_result is None:
            raise RuntimeError('Failed to find connectable device')
        return self.connect(**scan_result)

    def connect(self):
        self._connected = True

        return self

    def disconnect(self):
        self._connected = False

        return self
