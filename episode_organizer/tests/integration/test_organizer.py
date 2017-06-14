from time import sleep
from unittest.mock import MagicMock

import pytest

from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.daemon.storage_manager import StorageManager


class TestOrganizer:

    @pytest.fixture
    def watch_dir(self, tmpdir):
        return tmpdir.mkdir("watch")

    @pytest.fixture
    def storage_dir(self, tmpdir):
        return tmpdir.mkdir("storage")

    class setup_organizer:

        def __init__(self, watch_dir, filter, mapper, storage_manager, logger_mock=None):
            self.organizer = Organizer(watch_dir, filter, mapper, storage_manager)
            self.logger_mock = logger_mock

        def __enter__(self):
            self.organizer.start()
            if self.logger_mock:
                self.organizer.logger = self.logger_mock

            return self.organizer

        def __exit__(self, exc_type, exc_val, exc_tb):
            sleep(1)  # give a moment for the watcher to detect changes to the filesystem

            self.organizer.stop()
            self.organizer.join()

    def test_organize_DownloadedAnEpisodeFile(self, watch_dir, storage_dir):

        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir))):

            # New episode file was downloaded
            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

    def test_organize_DownloadEpisodeInsideADirectory(self, watch_dir, storage_dir, tmpdir):

        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir))):

            # New episode file was downloaded
            other_dir = tmpdir.mkdir("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]")
            episode_file = other_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv")
            episode_file.write("")
            other_dir.move(watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]"))

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]").check()

    def test_organize_FileAlreadyExistsInStorage(self, watch_dir, storage_dir):

        storage_dir.mkdir("Prison Break").mkdir("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        logger_mock = MagicMock()
        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)), logger_mock):

            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.warning.assert_called_once_with(
            "File 'Prison.Break.S05E09.720p.HDTV.x264.mkv' already exists in 'Prison Break/Season 05'")

    def test_organize_FilterRaisesOSError_FilesKeptInWatchDir(self, watch_dir, storage_dir):

        filter_mock = MagicMock()
        filter_mock.get_episode_file.side_effect = OSError("Permission denied")

        logger_mock = MagicMock()
        with self.setup_organizer(str(watch_dir), filter_mock, Mapper(), StorageManager(str(storage_dir)), logger_mock):

            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.exception.assert_called_once_with("Unexpected OS Error was raised")

    def test_organize_StorageManagerRaisesOSError_FilesKeptInWatchDir(self, watch_dir):

        storage_manager_mock = MagicMock()
        storage_manager_mock.store.side_effect = OSError("Permission denied")

        logger_mock = MagicMock()
        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), storage_manager_mock, logger_mock):

            watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.exception.assert_called_once_with("Unexpected OS Error was raised")

    def test_organize_NewFileIsNotAVideoFile_FilesKeptInWatchDir(self, watch_dir, storage_dir):

        logger_mock = MagicMock()
        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)), logger_mock):

            watch_dir.join("file.txt").write("")

        # Check the file was kept in the watch directory
        assert watch_dir.join("file.txt").check()
        logger_mock.warning.assert_called_once_with(
            "The path '%s' is not a video file" % str(watch_dir.join("file.txt")))

    def test_organize_NewDirectoryDoesNotContainAnyVideoFile_FilesKeptInWatchDir(self, watch_dir, storage_dir, tmpdir):

        logger_mock = MagicMock()
        with self.setup_organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)), logger_mock):

            # New episode file was downloaded
            other_dir = tmpdir.mkdir("other dir")
            other_dir.join("file.txt").write("")
            other_dir.move(watch_dir.join("other dir"))

        # Check the directory was kept in the watch directory
        assert watch_dir.join("other dir").check()
        logger_mock.warning.assert_called_once_with(
            "The directory '%s' does not contain any video file" % str(watch_dir.join("other dir")))

    def test_organize_StorageDirectoryIsDeleted_FilesKeptInWatchDirAndOrganizerExits(self, watch_dir, storage_dir):

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        organizer.start()

        logger_mock = MagicMock()
        organizer.logger = logger_mock

        storage_dir.remove()
        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)

        # Check the directory was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.error.assert_called_once_with("Storage directory was deleted")
        # Check the organizer exits
        organizer.join()
