from time import sleep
from unittest.mock import patch, MagicMock
from xmlrpc.client import ServerProxy, Fault

import pytest

from episode_organizer.daemon.configurator import Configurator
from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.daemon.storage_manager import StorageManager


class TestConfigurator:

    class System:
        """
        The setup_system __enter__ method return an instance of this class with all the components of the system
        that were initialized.
        """
        def __init__(self, organizer, configurator):
            self.organizer = organizer
            self.configurator = configurator

    class setup_system:

        def __init__(self, watch_dir, storage_dir, logger_mock=None, wait_before_stop=True):
            """
            :param watch_dir:           the watch directory provided to the organizer.
            :param storage_dir:         the storage directory provided to the organizer.
            :param logger_mock:         a mock object to be ser for the configurator's logger.
            :param wait_before_stop:    set to false to turnoff the wait time before stopping the services.
            """
            self.logger_mock = logger_mock
            self.wait_before_stop = wait_before_stop

            self.organizer = Organizer(watch_dir, Filter(), Mapper(), StorageManager(storage_dir))
            # Note config and config_file are mocks here because they are completely ignored
            self.configurator = Configurator(config=MagicMock(), config_file=MagicMock(), organizer=self.organizer)

        def __enter__(self):
            self.organizer.start()
            self.configurator.start()

            if self.logger_mock:
                Configurator.logger = self.logger_mock

            return TestConfigurator.System(self.organizer, self.configurator)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.configurator.stop()
            self.configurator.join()

            if self.wait_before_stop:
                sleep(1)  # give 1 second for the watcher to be notified by the filesystem

            self.configurator.stop()
            self.configurator.join()
            self.organizer.stop()
            self.organizer.join()

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDirToExistingDir_ChangesToNewDirAreDetected(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")

        logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), logger_mock) as system:

            # Configurator called to set a new watch directory
            system.configurator.set_watch_dir(str(new_watch_dir))

            # Someone creates a new file in the new watch directory
            new_watch_dir.join("file.txt").write("")

        # New file in the new watch directory is detected
        on_new_file_mock.assert_called_once_with(new_watch_dir.join("file.txt"))

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDirToNonExistingDir_ChangesToPreviousDirAreDetected(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.join("new_watch")  # note the use of 'join': the directory is not created

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock) as system:

            # The client tries to change the watch directory to an NON-existing directory, which will raise an error
            with pytest.raises(FileNotFoundError):
                system.configurator.set_watch_dir(str(new_watch_dir))

            # Afterwards, someone creates a new file in the previous watch directory
            watch_dir.join("file.txt").write("")

        # The newly created file is detected
        on_new_file_mock.assert_called_once_with(watch_dir.join("file.txt"))

        # And the configurator logged a warning indicating the error
        configurator_logger_mock.warning\
            .assert_called_once_with("Tried changing watch directory to '%s', but that directory did not exist. "
                                     "Kept previous watch directory" % str(new_watch_dir))

    def test_SetStorageDirToExistingDir_EpisodeFilesAreStoredInTheNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock) as system:

            # The client tries to change the storage directory to an existing directory
            system.configurator.set_storage_dir(str(new_storage_dir))

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # And the episode file was moved into the new storage directory
        assert new_storage_dir.join("Prison Break").join("Season 05")\
                              .join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

    def test_SetStorageDirToNonExistingDir_EpisodeFilesAreStillMovedIntoPreviousDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")  # note the use of 'join': the directory is not created

        configurator_logger_mock = MagicMock()
        with self.setup_system(str(watch_dir), str(storage_dir), configurator_logger_mock) as system:

            # The client tries to change the storage directory to an NON-existing directory, which will raise an error
            with pytest.raises(FileNotFoundError):
                system.configurator.set_storage_dir(str(new_storage_dir))

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # The episode file was still moved into the previous storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

        # And the configurator logged a warning indicating the error
        configurator_logger_mock.warning\
            .assert_called_once_with("Tried changing storage directory to '%s', but that directory did not exist. "
                                     "Kept previous storage directory" % str(new_storage_dir))
