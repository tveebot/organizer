import sys
from unittest.mock import patch

import pytest

from episode_organizer.config_client import EntryPoint


class TestEntrypoint:

    @staticmethod
    def set_input_args(args):
        sys.argv = ['script']
        sys.argv.extend(args)

    @patch.object(EntryPoint, 'setup_client')
    def test_GetValueWithoutSpecifyingTheHostOrPort_DefaultsToLocalhostAndPort8000(self, setup_client_mock):

        self.set_input_args(['-g', 'WatchDirectory'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('localhost', '35121')

    @patch.object(EntryPoint, 'setup_client')
    def test_SetValueWithoutSpecifyingTheHostOrPort_DefaultsToLocalhostAndPort8000(self, setup_client_mock):

        self.set_input_args(['-s', 'WatchDirectory', 'watch/'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('localhost', '35121')

    @patch.object(EntryPoint, 'setup_client')
    def test_GetValueWithHostMyHostNameAndPort5000_ClientIsSetupWithHostMyHostNameAndPort5000(self, setup_client_mock):

        self.set_input_args(['-g', 'WatchDirectory', '--host=my.host.name', '--port=5000'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('my.host.name', '5000')

    @patch.object(EntryPoint, 'setup_client')
    def test_SetValueWithHostMyHostNameAndPort5000_ClientIsSetupWithHostMyHostNameAndPort5000(self, setup_client_mock):

        self.set_input_args(['-s', 'WatchDirectory', 'watch/', '--host=my.host.name', '--port=5000'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('my.host.name', '5000')

    @patch.object(EntryPoint, 'setup_client')
    def test_GetValueWithHostMyHostName_ClientIsSetupWithHostMyHostNameAndDefaultPort(self, setup_client_mock):

        self.set_input_args(['-g', 'WatchDirectory', '--host=my.host.name'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('my.host.name', '35121')

    @patch.object(EntryPoint, 'setup_client')
    def test_SetValueWithHostMyHostName_ClientIsSetupWithHostMyHostNameAndDefaultPort(self, setup_client_mock):
        self.set_input_args(['-s', 'WatchDirectory', 'watch/', '--host=my.host.name'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('my.host.name', '35121')

    @patch.object(EntryPoint, 'setup_client')
    def test_GetValueWithPort5000_ClientIsSetupWithDefaultAndPort5000(self, setup_client_mock):

        self.set_input_args(['-g', 'WatchDirectory', '--port=5000'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('localhost', '5000')

    @patch.object(EntryPoint, 'setup_client')
    def test_SetValueWithPort5000_ClientIsSetupWithDefaultAndPort5000(self, setup_client_mock):
        self.set_input_args(['-s', 'WatchDirectory', 'watch/', '--port=5000'])
        EntryPoint().main()

        setup_client_mock.assert_called_once_with('localhost', '5000')

    def test_SetupClient_WithValidHostnameAndPort_Succeeds(self):

        EntryPoint().setup_client('my.host.name', '5000')

    def test_SetupClient_WithInvalidHostname_RaisesValueError(self):

        with pytest.raises(ValueError) as exception_info:

            EntryPoint().setup_client('my:host:name', '5000')

        assert str(exception_info.value) == "Hostname 'my:host:name' is not valid"

    def test_SetupClient_WithInvalidIntegerPort_RaisesValueError(self):

        with pytest.raises(ValueError) as exception_info:
            EntryPoint().setup_client('my.host.name', '65555')

        assert str(exception_info.value) == "Port '65555' is not valid"

    def test_SetupClient_WithInvalidStringPort_RaisesValueError(self):

        with pytest.raises(ValueError) as exception_info:
            EntryPoint().setup_client('my.host.name', 'port')

        assert str(exception_info.value) == "Port 'port' is not valid"
