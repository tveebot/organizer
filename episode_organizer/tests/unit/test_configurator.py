from unittest.mock import MagicMock, patch

import pytest

from episode_organizer.daemon.configurator import Configurator
from episode_organizer.daemon.configuration import Configuration
from episode_organizer.tests import defaults


# noinspection PyTypeChecker
class TestConfigurator:

    @pytest.fixture
    def config_file(self, tmpdir):
        return str(tmpdir.join("config.ini"))

    def test_SetWatchDir_ToExistingDir_WatchDirIsSetToNewDir(self, tmpdir, config_file):

        new_watch_dir = tmpdir.mkdir("new_watch")
        configuration = Configuration.from_dict({
            'WatchDirectory': "/watch/dir"
        })
        configurator = Configurator(config_file, configuration, organizer=MagicMock())

        configurator.set_config('WatchDirectory', str(new_watch_dir))

        assert configurator.get_config('WatchDirectory') == str(new_watch_dir)

    def test_SetWatchDir_ToExistingDir_OrganizerIsInformedOfTheChange(self, tmpdir, config_file):

        new_watch_dir = tmpdir.mkdir("new_watch")
        configuration = Configuration.from_dict({
            'WatchDirectory': "/watch/dir"
        })
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        configurator.set_config('WatchDirectory', str(new_watch_dir))

        organizer_mock.set_watch_dir.assert_called_once_with(str(new_watch_dir))

    def test_SetWatchDir_ToNonExistingDir_WatchDirIsKept(self, config_file):

        configuration = Configuration.from_dict({
            'WatchDirectory': "/watch/dir"
        })
        # When the directory does not exist the organizer raises FileNotFoundError
        organizer_stub = MagicMock()
        organizer_stub.set_watch_dir.side_effect = FileNotFoundError()
        configurator = Configurator(config_file, configuration, organizer_stub)

        with pytest.raises(FileNotFoundError):
            configurator.set_config('WatchDirectory', "/new/watch/dir")

        assert configurator.get_config('WatchDirectory') == "/watch/dir"

    @patch.object(Configuration, '__setitem__')
    def test_SetWatchDir_FailsToAccessConfigFile_RaisesOSErrorOrganizerIsNotChanged(
            self, config_setitem_stub, config_file):

        configuration = Configuration.from_dict({
            'WatchDirectory': "/watch/dir"
        })
        config_setitem_stub.side_effect = OSError()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        with pytest.raises(OSError):
            configurator.set_config('WatchDirectory', "/new/watch/dir")

        organizer_mock.set_watch_dir.assert_not_called()

    @patch.object(Configuration, '__setitem__')
    def test_SetWatchDir_FailsToCreateConfigFile_RaisesFileNotFoundError(self, config_setitem_stub, config_file):

        configuration = Configuration.from_dict({
            'WatchDirectory': "/watch/dir"
        })
        config_setitem_stub.side_effect = FileNotFoundError()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        with pytest.raises(FileNotFoundError):
            configurator.set_config('WatchDirectory', "/new/watch/dir")

        organizer_mock.set_watch_dir.assert_not_called()

    def test_SetStorageDir_ToExistingDir_StorageDirIsSetToNewDir(self, tmpdir, config_file):

        new_storage_dir = tmpdir.mkdir("new_storage")

        configuration = Configuration.from_dict({
            'StorageDirectory': "/storage/dir"
        })
        configurator = Configurator(config_file, configuration, organizer=MagicMock())

        configurator.set_config('StorageDirectory', str(new_storage_dir))

        assert configurator.get_config('StorageDirectory') == str(new_storage_dir)

    def test_SetStorageDir_ToExistingDir_OrganizerIsInformedOfTheChange(self, tmpdir, config_file):

        new_storage_dir = tmpdir.mkdir("new_storage")

        configuration = Configuration.from_dict({
            'StorageDirectory': "/storage/dir"
        })
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        configurator.set_config('StorageDirectory', str(new_storage_dir))

        organizer_mock.set_storage_dir.assert_called_once_with(str(new_storage_dir))

    def test_SetStorageDir_ToNonExistingDir_StorageDirIsKept(self, tmpdir, config_file):

        configuration = Configuration.from_dict({
            'StorageDirectory': "/storage/dir"
        })
        # When the directory does not exist the organizer raises FileNotFoundError
        organizer_stub = MagicMock()
        organizer_stub.set_storage_dir.side_effect = FileNotFoundError()
        configurator = Configurator(config_file, configuration, organizer_stub)

        with pytest.raises(FileNotFoundError):
            configurator.set_config('StorageDirectory', "/new/storage/dir")

        assert configurator.get_config('StorageDirectory') == "/storage/dir"

    @patch.object(Configuration, '__setitem__')
    def test_SetStorageDir_FailsToAccessConfigFile_RaisesOSError(self, config_setitem_stub, config_file):

        configuration = Configuration.from_dict({
            'StorageDirectory': "/storage/dir"
        })
        config_setitem_stub.side_effect = OSError()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        with pytest.raises(OSError):
            configurator.set_config('StorageDirectory', "/new/storage/dir")

        organizer_mock.set_storage_dir.assert_not_called()

    @patch.object(Configuration, '__setitem__')
    def test_SetStorageDir_FailsToCreateConfigFile_RaisesFileNotFoundError(self, config_setitem_stub, config_file):

        configuration = Configuration.from_dict({
            'StorageDirectory': "/storage/dir"
        })
        config_setitem_stub.side_effect = FileNotFoundError()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        with pytest.raises(FileNotFoundError):
            configurator.set_config('StorageDirectory', "/new/storage/dir")

        organizer_mock.set_storage_dir.assert_not_called()

    def test_SetInvalidKey_RaisesKeyError(self, config_file):

        configuration = Configuration()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, configuration, organizer_mock)

        with pytest.raises(KeyError) as exception_info:
            configurator.set_config('InvalidKey', "some value")

        assert "Key 'InvalidKey' is invalid" in str(exception_info.value)

        organizer_mock.set_storage_dir.assert_not_called()

    def test_SetValueForKeyThatCanNotBeEdited_RaisesKeyError(self, config_file):

        config = Configuration()
        organizer_mock = MagicMock()
        configurator = Configurator(config_file, config, organizer_mock)

        with pytest.raises(KeyError) as exception_info:
            configurator.set_config('ConfiguratorPort', '8000')

        assert "Key 'ConfiguratorPort' is invalid" in str(exception_info.value)

        organizer_mock.set_storage_dir.assert_not_called()
        assert config['ConfiguratorPort'] == defaults.config['ConfiguratorPort']
