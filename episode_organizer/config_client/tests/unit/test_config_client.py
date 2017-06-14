from unittest.mock import patch

import pytest

from episode_organizer.config_client.config_client import ConfigClient


class TestConfigClient:

    @pytest.fixture
    def any_address(self):
        return 'localhost', 8000

    @patch.object(ConfigClient, 'set_watch_dir')
    def test_SetConfig_KeyWatchDirectory_CallsSetWatchDirectory(self, mock_set_watch_dir, any_address):
        client = ConfigClient(any_address)

        client.set_config(key='WatchDirectory', value='new_watch')

        mock_set_watch_dir.assert_called_once_with('new_watch')

    @patch.object(ConfigClient, 'set_storage_dir')
    def test_SetConfig_KeyStorageDirectory_CallsSetStorageDirectory(self, mock_set_storage_dir, any_address):
        client = ConfigClient(any_address)

        client.set_config(key='StorageDirectory', value='new_storage')

        mock_set_storage_dir.assert_called_once_with('new_storage')
