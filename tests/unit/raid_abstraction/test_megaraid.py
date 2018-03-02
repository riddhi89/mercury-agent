import json
import os

import mock

from mercury.common.helpers.cli import CLIResult
from mercury_agent.hardware.drivers.megaraid import MegaRAIDActions, \
    MegaRaidSASDriver
from mercury_agent.hardware.raid.abstraction.api import RAIDAbstractionException

from ..base import MercuryAgentUnitTest


def get_storcli_dall_show(c):
    """ Gets data from json resource

    :param c: unused
    :return:
    """
    del c
    with open(os.path.join(os.path.dirname(__file__),
                           '../resources/storcli_dall_show.json')) as fp:
        data = json.load(fp)

        controller_list = []
        for controller in data['Controllers']:
            # Account for some crazy JSON schema
            controller_list.append(
                controller['Response Data']['Response Data']
            )

        return controller_list


def get_controllers():
    """ Gets controller information from json resource
    :return:
    """
    with open(os.path.join(os.path.dirname(__file__),
                           '../resources/storcli.json')) as fp:
        return [c['Response Data'] for c in json.load(fp)['Controllers']]


class DummyMegaRAIDActions(MegaRAIDActions):
    """ A dummy megaraid actions driver for easier patching """

    def __init__(self):
        super(MegaRAIDActions, self).__init__()
        self.storcli = mock.Mock()

        # controllers is a property
        self.storcli.controllers = get_controllers()

        self.storcli.get_disk_group = get_storcli_dall_show


class TestMegaRAIDActions(MercuryAgentUnitTest):
    """ MegaRAIDActions Test Case """

    def setUp(self):
        """ Instantiates a dummy module for use in test methods """
        super(TestMegaRAIDActions, self).setUp()

        self.dummy_actions = DummyMegaRAIDActions()

    def test_transform_configuration(self):
        """ Test overall transform operations """
        configuration = self.dummy_actions.transform_configuration(0)
        self.assertTrue(len(configuration['arrays']) == 2)
        self.assertEqual(configuration['arrays'][0]['free_space'], 0)
        self.assertEqual(
            configuration['arrays'][1]['physical_drives'][1]['extra']
            ['address'], '32:2')

        self.assertEqual(
            MegaRAIDActions.get_array_index_by_dg(
                configuration['arrays'], 1), 1)

        self.assertEqual(
            MegaRAIDActions.get_array_index_by_dg(
                configuration['arrays'], 99), -1)

    def test_without_available_drives(self):
        dg_info = get_storcli_dall_show(0)

        del dg_info[0]['UN-CONFIGURED DRIVE LIST']
        new_dummy_actions = DummyMegaRAIDActions()
        new_dummy_actions.storcli.get_disk_group = mock.Mock()
        new_dummy_actions.storcli.get_disk_group.return_value = dg_info

        configuration = new_dummy_actions.transform_configuration(0)
        self.assertFalse(configuration['unassigned'])
        self.assertFalse(configuration['spares'])

    def test_with_global_hotspare(self):
        """ Convert stored data so that it contains a GHS"""
        dg_info = get_storcli_dall_show(0)
        for drive in dg_info[0]['UN-CONFIGURED DRIVE LIST']:
            if drive['State'] == 'DHS':
                drive['State'] = 'GHS'
                drive['DG'] = '-'

        new_dummy_actions = DummyMegaRAIDActions()
        new_dummy_actions.storcli.get_disk_group = mock.Mock()
        new_dummy_actions.storcli.get_disk_group.return_value = dg_info

        configuration = new_dummy_actions.transform_configuration(0)

        self.assertEqual(configuration['spares'][0]['extra']['spare_type'],
                         'global')

    def test_with_no_hotspare(self):
        dg_info = get_storcli_dall_show(0)
        for drive in dg_info[0]['UN-CONFIGURED DRIVE LIST']:
            if drive['State'] in DummyMegaRAIDActions.hotspare_map:
                drive['State'] = 'UGood'  # UGood, bro?
                drive['DG'] = '-'
        new_dummy_actions = DummyMegaRAIDActions()
        new_dummy_actions.storcli.get_disk_group = mock.Mock()
        new_dummy_actions.storcli.get_disk_group.return_value = dg_info
        configuration = new_dummy_actions.transform_configuration(0)
        self.assertFalse(configuration['spares'])

    def test_transform_adapter_info(self):
        adapter_info = self.dummy_actions.transform_adapter_info(0)
        self.assertEqual(adapter_info['name'], 'PERC 6/i Integrated')
        self.assertEqual(MegaRAIDActions.get_controller_id(adapter_info),
                         0)
        self.assertRaises(RAIDAbstractionException,
                          self.dummy_actions.transform_adapter_info, *(100,))

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    @mock.patch('mercury_agent.hardware.drivers.megaraid.get_configuration')
    def test_real_init(self, mock_get_configuration, mock_cli):
        """ Tests real class __init__ method

        :param mock_get_configuration:
        :param mock_cli:
        :return:
        """
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        mock_get_configuration.return_value = {}

        assert MegaRAIDActions()

    def test_get_vendor_info_static(self):
        """ Tests get_vendor_info static method"""
        adapter = {
            'Basics': {},
            'Version': {},
            'Bus': {},
            'Status': {},
            'Supported Adapter Operations': {},
            'Supported PD Operations': {},
            'Supported VD Operations': {}
        }
        result = MegaRAIDActions.get_vendor_info(adapter)

        keys = [
            'general',
            'version_info',
            'bus',
            'status',
            'supported_adapter_ops',
            'supported_pd_ops',
            'supported_vd_ops',
            'bbu_info',
        ]

        missing = []
        for key in keys:
            if key not in result:
                missing.append(key)

        self.assertFalse(missing, 'Missing keys in output {}'.format(missing))

    def test_sort_drives_static(self):
        """ Test drive sorting  """
        drives = [
            {
                'extra':
                    {
                        'drive_id': 10
                    }
            },
            {
                'extra':
                    {
                        'drive_id': 5
                    }
            },
            {
                'extra':
                    {
                        'drive_id': 7
                    }
            },
            {
                'extra':
                    {
                        'drive_id': 0
                    }
            },
        ]

        MegaRAIDActions.sort_drives(drives)

        self.assertEqual(drives[0]['extra']['drive_id'], 0)
        self.assertEqual(drives[1]['extra']['drive_id'], 5)
        self.assertEqual(drives[2]['extra']['drive_id'], 7)
        self.assertEqual(drives[3]['extra']['drive_id'], 10)

    def test_create(self):
        """ Test create implementation """
        # Data does not have available drives, create one
        dg_info = get_storcli_dall_show(0)

        for drive in dg_info[0]['UN-CONFIGURED DRIVE LIST']:
            drive['State'] = 'UGood'
            drive['DG'] = '-'

        new_dummy_actions = DummyMegaRAIDActions()
        new_dummy_actions.storcli.get_disk_group = mock.Mock()
        new_dummy_actions.storcli.get_disk_group.return_value = dg_info

        adapter_info = new_dummy_actions.transform_adapter_info(0)
        drives = new_dummy_actions.get_drives_from_selection(0, [3])

        new_dummy_actions.create(adapter_info, 0, drives=drives)

        for drive in drives:
            drive['extra']['vendor_state'] = 'UBad'

        self.assertRaises(RAIDAbstractionException, new_dummy_actions.create,
                          *(adapter_info, 0, drives))

    def test_delete_logical_drive(self):
        """ Test delete_logical_drive implementation """
        self.dummy_actions.storcli.delete = mock.Mock()

        self.dummy_actions.delete_logical_drive(0, 0, 0)

        self.dummy_actions.storcli.delete.assert_called_with(**{
            'controller': 0,
            'virtual_drive': 0
        })

        self.assertRaises(RAIDAbstractionException,
                          self.dummy_actions.delete_logical_drive,
                          *(0, 0, 99))

    def test_clear_configuration(self):
        self.dummy_actions.storcli.delete = mock.Mock()
        self.dummy_actions.clear_configuration(0)
        self.dummy_actions.storcli.delete.assert_called_with(
            **{
                'controller': 0,
                'virtual_drive': 'all'
            }
        )

    def test_add_spares(self):
        """ Test create implementation """
        # Data does not have available drives, create one
        dg_info = get_storcli_dall_show(0)

        for drive in dg_info[0]['UN-CONFIGURED DRIVE LIST']:
            drive['State'] = 'UGood'
            drive['DG'] = '-'

        new_dummy_actions = DummyMegaRAIDActions()
        new_dummy_actions.storcli.get_disk_group = mock.Mock()
        new_dummy_actions.storcli.get_disk_group.return_value = dg_info

        new_dummy_actions.storcli.add_hotspare = mock.Mock()

        new_dummy_actions.add_spares(0, [3])

        new_dummy_actions.storcli.add_hotspare.assert_called_with(**{
            'controller': 0,
            'enclosure': 32,
            'slot': 3,
            'disk_groups': []
        })

        new_dummy_actions.add_spares(0, [3], [0])

        new_dummy_actions.storcli.add_hotspare.assert_called_with(**{
            'controller': 0,
            'enclosure': 32,
            'slot': 3,
            'disk_groups': [0]
        })

        self.assertRaises(RAIDAbstractionException,
                          new_dummy_actions.add_spares,
                          *(0, [3], [99]))


class MercuryMegaRaidDSDriverTest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercuryMegaRaidDSDriverTest, self).setUp()
        self.pci_data = [{'class_id': '0104',
                          'class_name': 'RAID bus controller',
                          'device_id': '005d',
                          'device_name': 'MegaRAID SAS-3 3108 [Invader]',
                          'driver': 'megaraid_sas',
                          'revision': '02',
                          'sdevice_id': '1f49',
                          'sdevice_name': 'PERC H730 Mini',
                          'slot': '02:00.0',
                          'svendor_id': '1028',
                          'svendor_name': 'Dell',
                          'vendor_id': '1000',
                          'vendor_name': 'LSI Logic / Symbios Logic'}]

    def test_probe(self):
        self.assertEqual(MegaRaidSASDriver.probe(self.pci_data), ['02:00.0'])

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    @mock.patch('mercury_agent.hardware.drivers.megaraid.get_configuration')
    def test_inspect(self, mock_cli, mock_get_configuration):
        driver = MegaRaidSASDriver(['02:00.0'])
        driver.handler = mock.Mock()
        driver.handler.get_adapter_info = mock.Mock()

        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        mock_get_configuration.return_value = {}

        driver.inspect()

        driver.handler.get_adapter_info.assert_called_with(0)
