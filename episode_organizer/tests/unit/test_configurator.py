from configparser import ConfigParser
from unittest.mock import MagicMock

import pytest

from episode_organizer.configurator import Configurator
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


class TestConfigurator:

    def configurator(self, watch_dir, storage_dir=None, config=MagicMock(), config_file=MagicMock()):

        storage_manager = StorageManager(str(storage_dir)) if storage_dir is not None else None

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), None, None, storage_manager)

        return Configurator(config, config_file, organizer)

    def test_SetWatchDirToExistingDir_WatchDirWasSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        new_watch_dir = tmpdir.mkdir("new_watch")
        configurator = self.configurator(str(watch_dir))

        configurator.set_watch_dir(str(new_watch_dir))

        assert configurator.watch_dir() == str(new_watch_dir)

    def test_SetWatchDirToNonExistingDir_RaiseFileNotFoundAndKeepsWatchDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        new_watch_dir = tmpdir.join("new_watch")
        configurator = self.configurator(str(watch_dir))

        with pytest.raises(FileNotFoundError):
            configurator.set_watch_dir(str(new_watch_dir))

        assert configurator.watch_dir() == str(watch_dir)

    def test_SetStorageDirToExistingDir_StorageDirWasSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")
        configurator = self.configurator(str(watch_dir), str(storage_dir))

        configurator.set_storage_dir(str(new_storage_dir))

        assert configurator.storage_dir() == str(new_storage_dir)

    def test_SetStorageDirToNonExistingDir_RaiseFileNotFoundAndKeepsStorageDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")
        configurator = self.configurator(str(watch_dir), str(storage_dir))

        with pytest.raises(FileNotFoundError):
            configurator.set_storage_dir(str(new_storage_dir))

        assert configurator.storage_dir() == str(storage_dir)

    def test_SetNewWatchDir_ConfigDoesNotExist_FileIsCreatedAndWatchDirectoryParamIsSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Non-default config file does not exist yet
        config_file = tmpdir.join("config.ini")

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_watch_dir(str(new_watch_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new watch directory
        assert loaded_config['DEFAULT']['WatchDirectory'] == str(new_watch_dir)

    def test_SetNewWatchDir_ConfigExistsButDoesNotDefineWatchDirectory_WatchDirectoryParamIsSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Config file currently does not define the WatchDirectory parameter - the default is being used
        config_file = tmpdir.join("config.ini")
        config_file.write("[DEFAULT]\n"
                          "StorageDirectory = %s" % str(storage_dir))
        config.read(str(config_file))

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_watch_dir(str(new_watch_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new watch directory
        assert loaded_config['DEFAULT']['WatchDirectory'] == str(new_watch_dir)

    def test_SetNewStorageDir_ConfigDoesNotExist_FileIsCreatedAndStorageDirectoryParamIsSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Non-default config file does not exist yet
        config_file = tmpdir.join("config.ini")

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_storage_dir(str(new_storage_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new storage directory
        assert loaded_config['DEFAULT']['StorageDirectory'] == str(new_storage_dir)

    def test_SetNewStorageDir_ConfigExistsButDoesNotDefineStorageDir_StorageDirectoryParamIsSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Config file currently does not define the WatchDirectory parameter - the default is being used
        config_file = tmpdir.join("config.ini")
        config_file.write("[DEFAULT]\n"
                          "WatchDirectory = %s" % str(watch_dir))
        config.read(str(config_file))

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_storage_dir(str(new_storage_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new storage directory
        assert loaded_config['DEFAULT']['StorageDirectory'] == str(new_storage_dir)

    def test_SetNewWatchDir_ConfigAlreadyDefinesSomeWatchDir_WatchDirectoryParamIsUpdatedToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Config file currently defines the WatchDirectory parameter - the default is being used
        config_file = tmpdir.join("config.ini")
        config_file.write("[DEFAULT]\n"
                          "WatchDirectory = %s"
                          "StorageDirectory = %s\n" % (str(watch_dir), str(storage_dir)))
        config.read(str(config_file))

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_watch_dir(str(new_watch_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new watch directory
        assert loaded_config['DEFAULT']['WatchDirectory'] == str(new_watch_dir)

    def test_SetNewStorageDir_ConfigAlreadyDefinesSomeStorageDir_StorageDirectoryParamIsUpdatedToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")

        # Using the default config file
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        # Config file currently defines the WatchDirectory parameter - the default is being used
        config_file = tmpdir.join("config.ini")
        config_file.write("[DEFAULT]\n"
                          "WatchDirectory = %s"
                          "StorageDirectory = %s\n" % (str(watch_dir), str(storage_dir)))
        config.read(str(config_file))

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config, str(config_file))

        configurator.set_storage_dir(str(new_storage_dir))

        loaded_config = ConfigParser()
        loaded_config.read(str(config_file))

        # The config file was updated to the new storage directory
        assert loaded_config['DEFAULT']['StorageDirectory'] == str(new_storage_dir)

    def test_SetWatchDirToNonExistingDir_ConfigWasNotUpdated(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.join("new_watch")

        config_file = tmpdir.join("config.ini")
        config_mock = MagicMock()

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config_mock, str(config_file))

        with pytest.raises(FileNotFoundError):
            configurator.set_watch_dir(str(new_watch_dir))

        config_mock.write.assert_not_called()

    def test_SetStorageDirToNonExistingDir_ConfigWasNotUpdated(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")

        config_file = tmpdir.join("config.ini")
        config_mock = MagicMock()

        # noinspection PyTypeChecker
        configurator = self.configurator(str(watch_dir), str(storage_dir), config_mock, str(config_file))

        with pytest.raises(FileNotFoundError):
            configurator.set_storage_dir(str(new_storage_dir))

        config_mock.write.assert_not_called()
