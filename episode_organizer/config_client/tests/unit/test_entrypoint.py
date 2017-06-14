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
