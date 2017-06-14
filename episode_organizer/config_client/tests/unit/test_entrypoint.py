import sys
from unittest.mock import patch

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

