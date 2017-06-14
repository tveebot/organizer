from time import sleep
from unittest.mock import patch

import pytest

from episode_organizer.daemon._configurator import Configurator
from episode_organizer.daemon.configuration import Configuration
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

    # noinspection PyArgumentList
    class setup_system:

        def __init__(self, watch_dir, storage_dir, config_file, wait_before_stop=True):
            """
            :param watch_dir:           the watch directory provided to the organizer.
            :param storage_dir:         the storage directory provided to the organizer.
            :param config_file:         the configuration file.
            :param wait_before_stop:    set to false to turnoff the wait time before stopping the services.
            """
            self.wait_before_stop = wait_before_stop

            self.organizer = Organizer(watch_dir, Filter(), Mapper(), StorageManager(storage_dir))

            config = Configuration.from_dict(config_file, {
                'WatchDirectory': watch_dir,
                'StorageDirectory': storage_dir,
            })

            self.configurator = Configurator(config, organizer=self.organizer)

        def __enter__(self):
            self.organizer.start()
            self.configurator.start()

            return TestConfigurator.System(self.organizer, self.configurator)

        def __exit__(self, exc_type, exc_val, exc_tb):

            if self.wait_before_stop:
                sleep(1)  # give 1 second for the watcher to be notified by the filesystem

            self.configurator.stop()
            self.configurator.join()
            self.organizer.stop()
            self.organizer.join()

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDir_ToExistingDir_ChangesToNewDirAreDetected(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.mkdir("new_watch")
        config_file = tmpdir.join("config.ini")

        with self.setup_system(str(watch_dir), str(storage_dir), str(config_file)) as system:

            # Configurator called to set a new watch directory
            system.configurator.set_config('WatchDirectory', str(new_watch_dir))

            # Someone creates a new file in the new watch directory
            new_watch_dir.join("file.txt").write("")

        # New file in the new watch directory is detected
        on_new_file_mock.assert_called_once_with(new_watch_dir.join("file.txt"))

    @patch.object(Organizer, 'on_new_file')
    def test_SetWatchDir_ToNonExistingDir_ChangesToPreviousDirAreDetected(self, on_new_file_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_watch_dir = tmpdir.join("new_watch")  # note the use of 'join': the directory is not created
        config_file = tmpdir.join("config.ini")

        with self.setup_system(str(watch_dir), str(storage_dir), str(config_file)) as system:

            # The client tries to change the watch directory to an NON-existing directory, which will raise an error
            with pytest.raises(FileNotFoundError):
                system.configurator.set_config('WatchDirectory', str(new_watch_dir))

            # Afterwards, someone creates a new file in the previous watch directory
            watch_dir.join("file.txt").write("")

        # The newly created file is detected
        on_new_file_mock.assert_called_once_with(watch_dir.join("file.txt"))

    def test_SetStorageDir_ToExistingDir_EpisodeFilesAreStoredInTheNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")
        config_file = tmpdir.join("config.ini")

        with self.setup_system(str(watch_dir), str(storage_dir), str(config_file)) as system:

            # The client tries to change the storage directory to an existing directory
            system.configurator.set_config('StorageDirectory', str(new_storage_dir))

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # And the episode file was moved into the new storage directory
        assert new_storage_dir.join("Prison Break").join("Season 05")\
                              .join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

    def test_SetStorageDir_ToNonExistingDir_EpisodeFilesAreStillMovedIntoPreviousDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")  # note the use of 'join': the directory is not created
        config_file = tmpdir.join("config.ini")

        with self.setup_system(str(watch_dir), str(storage_dir), str(config_file)) as system:

            # The client tries to change the storage directory to an NON-existing directory, which will raise an error
            with pytest.raises(FileNotFoundError):
                system.configurator.set_config('StorageDirectory', str(new_storage_dir))

            # Someone creates a new episode file in the watch directory
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # The episode file was still moved into the previous storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
