# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

from mercury_agent.configuration import get_configuration
from mercury_agent.hardware.drivers import DriverBase, driver
from mercury_agent.hardware.obm.ipmitool import (
    IPMIToolDrac,
    IPMIToolHP,
)

from mercury_agent.hardware.obm.racadm import SimpleRAC


log = logging.getLogger(__name__)


class IPMIDriverBase(DriverBase):
    name = 'ipmi'
    driver_type = 'bmc'
    wants = ''

    @classmethod
    def probe(cls, context_data):
        raise NotImplementedError

    def inspect(self):
        return {
            'network': self.handler.net_info,
            'system': self.handler.bmc_info
        }


@driver()
class HPILODriver(IPMIDriverBase):
    name = 'ilo'
    _handler = IPMIToolHP
    wants = 'pci'

    PCI_DEVICE_IDS = [
        "3306"  # Integrated Lights-Out Standard Slave Instrumentation & System
                # Support
    ]

    @classmethod
    def probe(cls, context_data):
        for pci_device in context_data:
            for my_device_id in cls.PCI_DEVICE_IDS:
                if pci_device['device_id'] == my_device_id:
                    return True
        return False


@driver()
class DRACDriver(IPMIDriverBase):
    name = 'drac'
    _handler = IPMIToolDrac
    wants = 'dmi'

    @classmethod
    def probe(cls, context_data):
        """ Tests that the server is a dell variant and has a compatible DRAC
        interface

        :param context_data: DMI information
        :return:
        """
        if context_data['sys_vendor'] == 'Dell Inc.':
            simple_rac = SimpleRAC(
                get_configuration().agent.hardware.obm.racadm_path
            )
            if 'System Information' in simple_rac.getsysinfo:
                return True
        return False
