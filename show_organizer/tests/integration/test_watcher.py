import os
from contextlib import contextmanager
from time import sleep
from unittest.mock import MagicMock

import pytest

# noinspection PyProtectedMember
from show_organizer.watch_handler import _BaseHandler
from show_organizer.watcher import Watcher


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
        yield

        watcher.stop()

    def test_FileIsCreated_WatcherCallsHandlersOnNewFileMethod(self, watch_handler_mock, tmpdir):

        with self.setup_watcher(str(tmpdir), watch_handler_mock):

            tmpdir.join("file").write("")
            sleep(1)  # Give some time for the watcher to receive information from the filesystem

            watch_handler_mock.on_new_file.assert_called_once_with(os.path.join(str(tmpdir), "file"))

    def test_DirectoryIsCreated_WatcherCallsHandlersOnNewDirectoryMethod(self, watch_handler_mock, tmpdir):

        with self.setup_watcher(str(tmpdir), watch_handler_mock):

            tmpdir.mkdir("dir")
            sleep(1)  # Give some time for the watcher to receive information from the filesystem

            watch_handler_mock.on_new_directory.assert_called_once_with(os.path.join(str(tmpdir), "dir"))
