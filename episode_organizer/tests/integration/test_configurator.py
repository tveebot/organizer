from unittest.mock import patch
from time import sleep
from xmlrpc.client import ServerProxy

from episode_organizer.configurator import Configurator
from episode_organizer.filter import Filter
from episode_organizer.mapper import Mapper
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


class TestConfigurator:

    @patch.object(Organizer, 'on_new_file')
    def test_set_watch_dir(self, on_new_file_mock, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        configurator = Configurator(organizer)

        organizer.start()
        configurator.start()

        new_watch_dir = tmpdir.mkdir("new_watch")

        client = ServerProxy('http://localhost:8000', allow_none=True)

        # Change watch directory
        client.set_watch_dir(str(new_watch_dir))

        # Create a new file inside the new watched directory
        new_watch_dir.join("file.txt").write("")
        sleep(1)

        # Verify that the watcher detected it
        on_new_file_mock.assert_called_once_with(new_watch_dir.join("file.txt"))

        assert client.watch_dir() == str(new_watch_dir)

        configurator.stop()
        configurator.join()
        organizer.stop()
        organizer.join()
