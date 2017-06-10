from time import sleep
from unittest.mock import MagicMock, patch

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.organizer import Organizer
from show_organizer.storage_manager import StorageManager


class TestOrganizer:

    def test_organize_DownloadedAnEpisodeFile(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        organizer.start()

        # New episode file was downloaded
        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)

        organizer.stop()

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

    def test_organize_DownloadEpisodeInsideADirectory(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        organizer.start()

        # New episode file was downloaded
        other_dir = tmpdir.mkdir("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]")
        episode_file = other_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv")
        episode_file.write("")
        other_dir.move(watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]"))

        sleep(1)

        organizer.stop()

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not other_dir.check()

    def test_organize_FileAlreadyExistsInStorage(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        storage_dir.mkdir("Prison Break").mkdir("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)
        organizer.stop()

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.warning.assert_called_once_with(
            "File 'Prison.Break.S05E09.720p.HDTV.x264.mkv' already exists in 'Prison Break/Season 05'")

    def test_organize_FilterRaisesOSError_FilesAreKeptOnWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        filter_mock = MagicMock()
        filter_mock.get_episode_file.side_effect = OSError("Permission denied")

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), filter_mock, Mapper(), StorageManager(str(storage_dir)))
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)
        organizer.stop()

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.exception.assert_called_once_with("Unexpected OS Error was raised")

    def test_organize_StorageManagerRaisesOSError_FilesAreKeptOnWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")

        storage_manager_mock = MagicMock()
        storage_manager_mock.store.side_effect = OSError("Permission denied")

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), Filter(), Mapper(), storage_manager_mock)
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)
        organizer.stop()

        # Check the file was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.exception.assert_called_once_with("Unexpected OS Error was raised")

    def test_organize_NewFileIsNotAVideoFile_FilesAreKeptOnWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        watch_dir.join("file.txt").write("")

        sleep(1)
        organizer.stop()

        # Check the file was kept in the watch directory
        assert watch_dir.join("file.txt").check()
        logger_mock.error.assert_called_once_with(
            "The path '%s' is not a video file" % str(watch_dir.join("file.txt")))

    def test_organize_NewDirectoryDoesNotContainAnyVideoFile_FilesAreKeptOnWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        # New episode file was downloaded
        other_dir = tmpdir.mkdir("other dir")
        other_dir.join("file.txt").write("")
        other_dir.move(watch_dir.join("other dir"))

        sleep(1)
        organizer.stop()

        # Check the directory was kept in the watch directory
        assert watch_dir.join("other dir").check()
        logger_mock.error.assert_called_once_with(
            "The directory '%s' does not contain any video file" % str(watch_dir.join("other dir")))

    def test_organize_StorageDirectoryIsDeleted_FilesAreKeptOnWatchDirectoryAndOrganizerExits(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        # noinspection PyTypeChecker
        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        logger_mock = MagicMock()
        organizer.logger = logger_mock
        organizer.start()

        storage_dir.remove()
        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)

        # Check the directory was kept in the watch directory
        assert watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        logger_mock.error.assert_called_once_with("Storage directory was deleted")

        # Check the organizer exits
        organizer.join()
