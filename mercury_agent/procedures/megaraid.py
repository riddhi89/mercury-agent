# Copyright 2018 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging

from mercury_agent.capabilities import capability
from mercury_agent.backend_client import get_backend_client
from mercury_agent.hardware.drivers.drivers import driver_class_cache
from mercury_agent.inspector.inspect import global_device_info
from mercury_agent.inspector.inspectors.raid import raid_inspector


log = logging.getLogger(__name__)


def get_megaraid_driver():
    return driver_class_cache.get('megaraid_sas')


def has_megaraid_driver():
    return bool(get_megaraid_driver())


def update_inventory():
    backend_client = get_backend_client()
    raid_info = raid_inspector(global_device_info)
    mercury_id = global_device_info['mercury_id']

    log.debug('RAID configuration changed, updating inventory')
    backend_client.update(mercury_id, {'raid': raid_info})


def update_on_change(f):
    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)
        update_inventory()
        return result
    wrapped_f.__name__ = f.__name__
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f


@capability('megaraid_add',
            description='Create and array on a megaraid_sas based controller',
            kwarg_names=['controller', 'array_type', 'drives'],
            serial=True,
            dependency_callback=has_megaraid_driver,
            timeout=60,
            task_id_kwargs=True
            )
@update_on_change
def megaraid_add(controller,
                 array_type,
                 drives,
                 size=None,
                 pdperarray=None,
                 pdcache=None,
                 dimmerswitch=None,
                 io_mode='direct',
                 write_policy='wb',
                 read_policy='ra',
                 cachevd=False,
                 stripe_size=None,
                 spares=None,
                 cached_bad_bbu=False,
                 after_vd=None):
    """ Add virtual drive

    :param controller: Controller ID
    :param array_type:  r[0|1|5|6|10|50|60]
    :param drives: Drives specified with as EncID:drive,...
    :param size: Size of a drive in MB or None for maximum
    :param pdperarray: Specifies the number of physical drives per array. The
default value is automatically chosen.(0 to 16)
    :param pdcache: Enables or disables PD cache. (on|off|default)
    :param dimmerswitch: Specifies the power-saving policy. Sets to default
automatically. default: Logical device uses controller default power-saving
policy. automatic (auto): Logical device power savings managed by firmware.
none: No power-saving policy.
maximum (max): Logical device uses maximum power savings.
MaximumWithoutCaching (maxnocache): Logical device does not cache write to
maximize power savings.
    :param io_mode: cached|direct
    :param write_policy:wb|rt
    :param read_policy:ra|rt
    :param cachevd: enables or disables cachecade device support
    :param stripe_size: stripe size ( the amount of data writen before moving to
the next disk )
    :param spares: Numer drives allocated as hot spares
    :param cached_bad_bbu: Enable write caches even when the bbu is missing or
discharged
    :param after_vd: Specify an existing VD to add this new vd behind
    :return: AttributeString of command output
    """

    driver = get_megaraid_driver()

    log.info('Adding Array: /c{} RAID{} drives: {} size: {}'.format(
        controller,
        array_type,
        drives,
        size
    ))

    return driver.storcli.add(
        controller,
        array_type,
        drives,
        size=size,
        pdperarray=pdperarray,
        pdcache=pdcache,
        dimmerswitch=dimmerswitch,
        io_mode=io_mode,
        write_policy=write_policy,
        read_policy=read_policy,
        cachevd=cachevd,
        stripe_size=stripe_size,
        spares=spares,
        cached_bad_bbu=cached_bad_bbu,
        after_vd=after_vd,
    )


@capability('megaraid_delete',
            description='Delete megaraid based virtual drive',
            kwarg_names=['controller'],
            serial=True,
            dependency_callback=has_megaraid_driver,
            timeout=60,
            task_id_kwargs=True)
@update_on_change
def megaraid_delete(controller, virtual_drive='all'):
    """

    :param controller: Controller id or all
    :param virtual_drive: Virtual Drive id or all
    :return:
    """

    driver = get_megaraid_driver()
    log.info('Deleting virtual drive: {} on controller: {}'.format(
        controller, virtual_drive
    ))

    return driver.storcli.delete(controller, virtual_drive)
