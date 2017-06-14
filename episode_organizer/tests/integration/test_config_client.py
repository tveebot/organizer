from configparser import ConfigParser

import pytest

from episode_organizer.config_client.config_client import ConfigClient
from episode_organizer.daemon.configurator import Configurator
from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.daemon.storage_manager import StorageManager


class TestConfigClient:

    # context manager
    class setup_system:

        def __init__(self, watch_dir, storage_dir, config, config_file):
            organizer = Organizer(watch_dir, Filter(), Mapper(), StorageManager(storage_dir))
            self.configurator = Configurator(config, config_file, organizer)

        def __enter__(self):
            self.configurator.start()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.configurator.stop()
            self.configurator.join()

    def test_SetNewWatchDir_GetWatchDirReturnNewWatchDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        with self.setup_system(str(watch_dir), str(storage_dir), config, str(config_file)):

            # A client connects to the configurator
            client = ConfigClient(server_address=('localhost', 8000))

            # The client tries to change the watch directory to an existing directory
            client.set_config('WatchDirectory', str(new_watch_dir))

            # Check if the watch directory was changed
            assert client.get_config('WatchDirectory') == str(new_watch_dir)

    def test_SetWatchDirToNonExistingDir_RaisesFileNotFoundError(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.join("new_watch")

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        with self.setup_system(str(watch_dir), str(storage_dir), config, str(config_file)):

            # A client connects to the configurator
            client = ConfigClient(server_address=('localhost', 8000))

            with pytest.raises(FileNotFoundError) as exception_info:
                client.set_config(key='WatchDirectory', value=str(new_watch_dir))

            assert str(exception_info.value) == "New watch directory does not exist: %s" % str(new_watch_dir)

    def test_ServerIsDisconnected_RaisesConnectionRefusedError(self, tmpdir):

        client = ConfigClient(server_address=('localhost', 8000))

        with pytest.raises(ConnectionRefusedError):
            client.set_config(key='WatchDirectory', value="watch/")
