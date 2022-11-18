# This file is part of toy-motor-controller and licensed under the
# GNU Affero General Public License v3.0 only (See LICENSE.txt)
# SPDX-License-Identifier: AGPL-3.0-only

from .. import __version__

from .akogd_power_function import AkogdPowerFunctionRemoteControl
from .playmobil_racer import PlaymobilRacerRemoteControl


__all__ = (
    AkogdPowerFunctionRemoteControl,
    PlaymobilRacerRemoteControl,
)

__version__ = __version__
