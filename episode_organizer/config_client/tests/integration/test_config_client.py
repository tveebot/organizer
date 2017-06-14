from configparser import ConfigParser
from contextlib import contextmanager

from episode_organizer.config_client.config_client import ConfigClient
from episode_organizer.daemon.configurator import Configurator
from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.daemon.storage_manager import StorageManager


class TestConfigClient:

    # TODO connect to a valid server
    # TODO connection fails

    @contextmanager
    def setup_system(self, watch_dir, storage_dir, config, config_file):
        organizer = Organizer(watch_dir, Filter(), Mapper(), StorageManager(storage_dir))
        configurator = Configurator(config, config_file, organizer)
        configurator.start()
        yield

        configurator.stop()
        configurator.join()

    def test_SetNewWatchDir_GetWatchDirReturnNewWatchDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        config_file = tmpdir.join("config.ini")
        config = ConfigParser()
        config['DEFAULT']['WatchDirectory'] = str(watch_dir)
        config['DEFAULT']['StorageDirectory'] = str(storage_dir)

        with self.setup_system(str(watch_dir), str(storage_dir), config, config_file):

            # A client connects to the configurator
            client = ConfigClient(server_address=('localhost', 8000))

            # The client tries to change the watch directory to an existing directory
            client.set_config('WatchDirectory', str(new_watch_dir))

            # Check if the watch directory was changed
            assert client.get_config('WatchDirectory') == str(new_watch_dir)

