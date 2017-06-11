import os
from contextlib import contextmanager
from time import sleep
from unittest.mock import MagicMock

import pytest

# noinspection PyProtectedMember
from episode_organizer.watch_handler import _BaseHandler
from episode_organizer.watcher import Watcher


class TestWatcher:

    @pytest.fixture
    def watch_handler_mock(self):
        handler_mock = MagicMock()
        handler_mock.base_handler = _BaseHandler(handler_mock)
        return handler_mock

    @contextmanager
    def setup_watcher(self, watch_dir, watch_handler):
        watcher = Watcher(watch_dir)
        watcher.add_handler(watch_handler)
        watcher.start()
        yield watcher

        sleep(1)  # Give some time for the watcher to receive information from the filesystem

        watcher.stop()
        watcher.join()

    def test_FileIsCreated_NewFileIsDetected(self, watch_handler_mock, tmpdir):

        with self.setup_watcher(str(tmpdir), watch_handler_mock):

            tmpdir.join("file").write("")

        # was new file detected?
        watch_handler_mock.on_new_file.assert_called_once_with(os.path.join(str(tmpdir), "file"))

    def test_DirectoryIsCreated_NewDirectoryIsDetected(self, watch_handler_mock, tmpdir):

        with self.setup_watcher(str(tmpdir), watch_handler_mock):

            tmpdir.mkdir("dir")

        # was new directory detected?
        watch_handler_mock.on_new_directory.assert_called_once_with(os.path.join(str(tmpdir), "dir"))

    def test_ExistingFileIsMovedIntoTheWatchDirectory_NewFileIsDetected(self, watch_handler_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        other_dir = tmpdir.mkdir("other")
        new_file = other_dir.join("file")
        new_file.write("")

        with self.setup_watcher(str(watch_dir), watch_handler_mock):
            new_file.move(watch_dir.join("file"))

        # was new file detected?
        watch_handler_mock.on_new_file.assert_called_once_with(os.path.join(str(watch_dir), "file"))

    def test_ExistingDirectoryIsMovedIntoTheWatchDirectory_NewFileIsDetected(self, watch_handler_mock, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        other_dir = tmpdir.mkdir("other")
        new_dir = other_dir.mkdir("dir")
        new_dir.join("file").write("")

        with self.setup_watcher(str(watch_dir), watch_handler_mock):
            new_dir.move(watch_dir.join("dir"))

        # was new file detected?
        watch_handler_mock.on_new_directory.assert_called_once_with(os.path.join(str(watch_dir), "dir"))

    def test_ChangingWatchDir_WatcherDetectsChangesInNewWatchDir(self, watch_handler_mock, tmpdir):

        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.mkdir("watch2")

        with self.setup_watcher(str(old_watch_dir), watch_handler_mock) as watcher:
            watcher.change_watch_dir(str(new_watch_dir))

            new_watch_dir.join("file.txt").write("")

        # was new file detected?
        watch_handler_mock.on_new_file.assert_called_once_with(str(new_watch_dir.join("file.txt")))

        assert watcher.watch_dir == str(new_watch_dir)

    def test_ChangingWatchDir_WatcherDoesNotDetectNewFilesOnTheOldWatchDir(self, watch_handler_mock, tmpdir):

        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.mkdir("watch2")

        with self.setup_watcher(str(old_watch_dir), watch_handler_mock) as watcher:
            watcher.change_watch_dir(str(new_watch_dir))

            old_watch_dir.join("file.txt").write("")

        # was new file detected?
        watch_handler_mock.on_new_file.assert_not_called()

    def test_ChangingToNonExistingWatchDir_WatcherRaisesFileNotFoundAndKeepsWatchDir(self, watch_handler_mock, tmpdir):

        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.join("watch2")  # note the 'join': the directory is not created

        with self.setup_watcher(str(old_watch_dir), watch_handler_mock) as watcher:
            with pytest.raises(FileNotFoundError):
                watcher.change_watch_dir(str(new_watch_dir))

            old_watch_dir.join("file.txt").write("")

        # was new file detected?
        watch_handler_mock.on_new_file.assert_called_once_with(str(old_watch_dir.join("file.txt")))

        assert watcher.watch_dir == str(old_watch_dir)
