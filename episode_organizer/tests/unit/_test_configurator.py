from contextlib import contextmanager
from unittest.mock import MagicMock, mock_open, patch

import pytest

from episode_organizer.daemon._configurator import Configurator
from episode_organizer.daemon.configuration import Configuration


# noinspection PyTypeChecker
class TestConfigurator:

    @contextmanager
    def stub_out_open(self):
        with patch('episode_organizer.daemon.configuration.open', mock_open()):
            yield

    def test_SetWatchDir_ToExistingDir_WatchDirWasSetToNewDir(self, tmpdir):

        new_watch_dir = tmpdir.mkdir("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'WatchDirectory': "/watch/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            configurator.set_config('WatchDirectory', str(new_watch_dir))

            assert configurator.get_config('WatchDirectory') == str(new_watch_dir)

    def test_SetWatchDir_ToExistingDir_OrganizerWasInformedOfTheChange(self, tmpdir):

        new_watch_dir = tmpdir.mkdir("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'WatchDirectory': "/watch/dir"
            })
            organizer_mock = MagicMock()
            configurator = Configurator(configuration, organizer_mock)

            configurator.set_config('WatchDirectory', str(new_watch_dir))

            organizer_mock.set_watch_dir.assert_called_once_with(str(new_watch_dir))

    def test_SetWatchDir_ToNonExistingDir_WatchDirWasKept(self, tmpdir):

        new_watch_dir = tmpdir.join("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'WatchDirectory': "/watch/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(FileNotFoundError):
                configurator.set_config('WatchDirectory', str(new_watch_dir))

            assert configurator.get_config('WatchDirectory') == "/watch/dir"

    @patch.object(Configuration, '__setitem__')
    def test_SetWatchDir_FailsToAccessConfigFile_RaisesOSError(self, config_setitem_stub):

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'WatchDirectory': "/watch/dir"
            })
            config_setitem_stub.side_effect = OSError()
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(OSError):
                configurator.set_config('WatchDirectory', "/new/watch/dir")

    @patch.object(Configuration, '__setitem__')
    def test_SetWatchDir_FailsToCreateConfigFile_RaisesFileNotFoundError(self, config_setitem_stub):

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'WatchDirectory': "/watch/dir"
            })
            config_setitem_stub.side_effect = FileNotFoundError()
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(FileNotFoundError):
                configurator.set_config('WatchDirectory', "/new/watch/dir")

    def test_SetStorageDir_ToExistingDir_StorageDirWasSetToNewDir(self, tmpdir):

        new_storage_dir = tmpdir.mkdir("new_storage")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'StorageDirectory': "/storage/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            configurator.set_config('StorageDirectory', str(new_storage_dir))

            assert configurator.get_config('StorageDirectory') == str(new_storage_dir)

    def test_SetStorageDir_ToExistingDir_OrganizerWasInformedOfTheChange(self, tmpdir):

        new_storage_dir = tmpdir.mkdir("new_storage")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'StorageDirectory': "/storage/dir"
            })
            organizer_mock = MagicMock()
            configurator = Configurator(configuration, organizer_mock)

            configurator.set_config('StorageDirectory', str(new_storage_dir))

            organizer_mock.set_storage_dir.assert_called_once_with(str(new_storage_dir))

    def test_SetStorageDir_ToNonExistingDir_StorageDirWasKept(self, tmpdir):

        new_storage_dir = tmpdir.join("new_storage")

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'StorageDirectory': "/storage/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(FileNotFoundError):
                configurator.set_config('StorageDirectory', str(new_storage_dir))

            assert configurator.get_config('StorageDirectory') == "/storage/dir"

    @patch.object(Configuration, '__setitem__')
    def test_SetStorageDir_FailsToAccessConfigFile_RaisesOSError(self, config_setitem_stub):

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'StorageDirectory': "/storage/dir"
            })
            config_setitem_stub.side_effect = OSError()
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(OSError):
                configurator.set_config('StorageDirectory', "/new/storage/dir")

    @patch.object(Configuration, '__setitem__')
    def test_SetStorageDir_FailsToCreateConfigFile_RaisesFileNotFoundError(self, config_setitem_stub):

        with self.stub_out_open():

            configuration = Configuration.from_dict({
                'StorageDirectory': "/storage/dir"
            })
            config_setitem_stub.side_effect = FileNotFoundError()
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(FileNotFoundError):
                configurator.set_config('StorageDirectory', "/new/storage/dir")

    def test_SetInvalidKey_RaisesKeyError(self):

        with self.stub_out_open():

            configuration = Configuration()
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(KeyError) as exception_info:
                configurator.set_config('InvalidKey', "some value")

            assert "Key 'InvalidKey' is invalid" in str(exception_info.value)
