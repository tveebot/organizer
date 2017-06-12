from contextlib import contextmanager
from unittest.mock import patch, MagicMock
from time import sleep
from xmlrpc.client import ServerProxy, Fault

import pytest

from episode_organizer.configurator import Configurator
from episode_organizer.filter import Filter
from episode_organizer.mapper import Mapper
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


class TestConfigurator:

    @contextmanager
    def setup_system(self, watch_dir, storage_dir, configurator_logger_mock=None):
        organizer = Organizer(watch_dir, Filter(), Mapper(), StorageManager(storage_dir))
        configurator = Configurator(organizer)
        organizer.start()
        configurator.start()

        if configurator_logger_mock:
            Configurator.logger = configurator_logger_mock

        yield

        sleep(1)  # give 1 second for the watcher to be notified by the filesystem

        configurator.stop()
        configurator.join()
        organizer.stop()
        organizer.join()

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDirToAnExistingDir(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock):

            # A client connects to the configurator
            client = ServerProxy('http://localhost:8000', allow_none=True)

            # The client tries to change the watch directory to an existing directory
            client.set_watch_dir(str(new_watch_dir))

            # Check the server changed the watch directory
            assert client.watch_dir() == str(new_watch_dir)

            # Someone creates a new file in the new watch directory
            new_watch_dir.join("file.txt").write("")

        # Verify that the watcher detected the new created file
        on_new_file_mock.assert_called_once_with(new_watch_dir.join("file.txt"))

        # And configurator logs the change
        configurator_logger_mock.info\
            .assert_called_once_with("Watch directory was changed to: %s" % str(new_watch_dir))

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDirToAnNonExistingDir(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.join("new_watch")  # note the use of 'join': the directory is not created

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock):

            # A client connects to the configurator
            client = ServerProxy('http://localhost:8000', allow_none=True)

            with pytest.raises(Fault) as exception_info:
                # The client tries to change the watch directory to an NON-existing directory
                client.set_watch_dir(str(new_watch_dir))

            # Check that server raised FileNotFoundError and it did not change the work directory
            assert "class 'FileNotFoundError'" in str(exception_info.value)
            assert client.watch_dir() == str(watch_dir)

            # Someone creates a new file in the previous watch directory
            watch_dir.join("file.txt").write("")

        # The watcher detects the new file because it is still watching the same directory
        on_new_file_mock.assert_called_once_with(watch_dir.join("file.txt"))

        # And the configurator logged a warning indicating the error
        configurator_logger_mock.warning\
            .assert_called_once_with("Tried changing watch directory to '%s', but that directory did not exist. "
                                     "Kept previous watch directory" % str(new_watch_dir))

    def test_SetStorageDirToAnExistingDir_EpisodeFilesAreStoredInTheNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock):

            # A client connects to the configurator
            client = ServerProxy('http://localhost:8000', allow_none=True)

            # The client tries to change the storage directory to an existing directory
            client.set_storage_dir(str(new_storage_dir))

            # Check the server changed the storage directory
            assert client.storage_dir() == str(new_storage_dir)

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # And the episode file was moved into the new storage directory
        assert new_storage_dir.join("Prison Break").join("Season 05")\
                              .join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

        # And configurator logs the change
        configurator_logger_mock.info\
            .assert_called_once_with("Storage directory was changed to: %s" % str(new_storage_dir))

    def test_SetStorageDirToANonExistingDir_ClientReceivesFileNotFoundError(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")  # note the use of 'join': the directory is not created

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock):
            # A client connects to the configurator
            client = ServerProxy('http://localhost:8000', allow_none=True)

            with pytest.raises(Fault) as exception_info:
                # The client tries to change the storage directory to an NON-existing directory
                client.set_storage_dir(str(new_storage_dir))

            # Check that server raised FileNotFoundError and it did not change the work directory
            assert "class 'FileNotFoundError'" in str(exception_info.value)
            assert client.storage_dir() == str(storage_dir)

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # The episode file was moved into the previous storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

        # And the configurator logged a warning indicating the error
        configurator_logger_mock.warning\
            .assert_called_once_with("Tried changing storage directory to '%s', but that directory did not exist. "
                                     "Kept previous storage directory" % str(new_storage_dir))
