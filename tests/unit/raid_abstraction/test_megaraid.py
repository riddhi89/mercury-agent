import json
import os

import mock

from mercury.common.helpers.cli import CLIResult
from mercury_agent.hardware.drivers.megaraid import MegaRAIDActions

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

    def test_transform_adapter_info(self):
        adapter_info = self.dummy_actions.transform_adapter_info(0)
        self.assertEqual(adapter_info['name'], 'PERC 6/i Integrated')
        self.assertEqual(MegaRAIDActions.get_controller_id(adapter_info),
                         0)

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
