import sys
from unittest.mock import patch

from episode_organizer.config_client import EntryPoint


class TestEntrypoint:

    @patch.object(EntryPoint, 'setup_client')
    def test_GetValueWithoutSpecifyingTheHostOrPort_DefaultsToLocalhostAndPort8000(self, setup_client_mock):

        sys.argv = ['script', '-g', 'WatchDirectory']

        entrypoint = EntryPoint()
        entrypoint.main()

        setup_client_mock.assert_called_once_with('localhost', '35121')

    @patch.object(EntryPoint, 'setup_client')
    def test_SetValueWithoutSpecifyingTheHostOrPort_DefaultsToLocalhostAndPort8000(self, setup_client_mock):

        sys.argv = ['script', '-s', 'WatchDirectory', 'watch/']

        entrypoint = EntryPoint()
        entrypoint.main()

        setup_client_mock.assert_called_once_with('localhost', '35121')
