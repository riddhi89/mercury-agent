import mock
import os

from mercury.common.helpers.cli import CLIResult
from mercury_agent.hardware.raid.interfaces.megaraid import storcli

from ..base import MercuryAgentUnitTest


class StorcliTest(MercuryAgentUnitTest):
    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_run(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        s = storcli.Storcli()
        assert s.run('') == ''

        mock_cli.run.return_value = CLIResult('Error', '', 1)

        self.assertRaises(storcli.StorcliException, s.run, *('',))

        mock_cli.find_in_path.return_value = None

        self.assertRaises(storcli.StorcliException, storcli.Storcli)

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_run_json(self, mock_cli):
        with open(os.path.join(os.path.dirname(__file__),
                               '../resources/storcli.json')) as fp:
            json_data = fp.read()

        mock_cli.run.return_value = CLIResult(json_data, '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        s = storcli.Storcli()
        assert isinstance(s.run_json('/call show all'), dict)

        mock_cli.run.return_value = CLIResult('not_valid_json', '', 0)

        self.assertRaises(storcli.StorcliException, s.run_json, *('',))

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_controllers(self, mock_cli):
        with open(os.path.join(os.path.dirname(__file__),
                               '../resources/storcli.json')) as fp:
            json_data = fp.read()

        mock_cli.run.return_value = CLIResult(json_data, '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        s = storcli.Storcli()
        assert isinstance(s.controllers, list)

        mock_cli.run.return_value = CLIResult('{}', '', 0)

        def _wrapper():
            return s.controllers

        self.assertRaises(storcli.StorcliException, _wrapper)

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_delete(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'
        s = storcli.Storcli()
        assert s.delete(0) == ''

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_add(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'

        s = storcli.Storcli()
        assert s.add(0, 'r0', '32:0-1') == ''
        assert s.add(0, 'r10', '32:0-3', pdperarray=2) == ''

        self.assertRaises(storcli.StorcliException, s.add,
                          *(0, 'r10', '32:0-3'))

        with open(os.path.join(os.path.dirname(__file__),
                               '../resources/storcli_err.txt')) as fp:
            error_data = fp.read()

        mock_cli.run.return_value = CLIResult(error_data, '', 0)

        self.assertRaises(storcli.StorcliException, s.add, *(0, '', ''))

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_get_enclosures(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'

        s = storcli.Storcli()
        s.run_json = mock.Mock()
        s.run_json.return_value = {'Controllers': [{'Response Data': 'cheese'}]}

        self.assertEqual(s.get_enclosures(), ['cheese'])

        s.run_json.assert_called_with('/call/eall show all')

        s.get_enclosures(99)
        s.run_json.assert_called_with('/c99/eall show all')

        s.run_json.return_value = {}

        self.assertRaises(storcli.StorcliException, s.get_enclosures)

    def test_bad_command_status(self):
        self.assertRaises(storcli.StorcliException,
                          storcli.Storcli.check_command_status,
                          *({'Command Status': {
                              'Status': 'Nope',
                              'Description': 'Problems',
                              'Detailed Status': ['Things???']
                          }},))

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_get_disk_group(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'

        s = storcli.Storcli()
        s.run_json = mock.Mock()
        s.run_json.return_value = {
            'Controllers': [{
                'Command Status': {
                    'Status': 'Success'
                },
                'Response Data': {
                    'Response Data': {}
                }}]}

        s.get_disk_group()

        s.run_json.assert_called_with('/call/dall show all')

        s.get_disk_group(99, 100)
        s.run_json.assert_called_with('/c99/d100 show all')

    @mock.patch('mercury_agent.hardware.raid.interfaces.megaraid.storcli.cli')
    def test_add_hotspare(self, mock_cli):
        mock_cli.run.return_value = CLIResult('', '', 0)
        mock_cli.find_in_path.return_value = '/sbin/storcli64'

        s = storcli.Storcli()
        s.run = mock.Mock()

        s.add_hotspare(0, 32, 10)

        s.run.assert_called_with('/c0/e32/s10 add hotsparedrive')

        s.add_hotspare(0, 32, 10, [0, 1, 2])

        s.run.assert_called_with('/c0/e32/s10 add hotsparedrive DGs=0,1,2')
