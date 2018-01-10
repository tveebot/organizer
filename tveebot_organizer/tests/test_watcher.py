from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from time import sleep
from typing import cast
from unittest.mock import MagicMock

from pytest import raises

from tveebot_organizer.organizer import Organizer
from tveebot_organizer.watcher import Watcher


@contextmanager
def watching(watch_dir: Path):
    organizer_mock = MagicMock()
    watcher = Watcher(watch_dir, organizer=cast(Organizer, organizer_mock))
    watcher_thread = Thread(target=watcher.run_forever)
    watcher_thread.start()

    sleep(0.5)
    yield watcher, organizer_mock
    sleep(1)

    watcher.shutdown()
    watcher_thread.join()


class TestWatcher:

    def test_OrganizerIsCalledWhenAFileIsCreated(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")

        with watching(Path(watch_dir)) as (_, organizer_mock):
            watch_dir.join("file.txt").write("")

        organizer_mock.organize.assert_called_once_with(Path(watch_dir) / "file.txt")

    def test_OrganizerIsCalledWhenADirectoryIsCreated(self, tmpdir):
        watch_dir = tmpdir

        with watching(Path(watch_dir)) as (_, organizer_mock):
            watch_dir.mkdir("dir")

        organizer_mock.organize.assert_called_once_with(Path(watch_dir) / "dir")

    def test_OrganizerIsCalledWhenExistingFileIsMovedIntoTheWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        other_dir = tmpdir.mkdir("other")
        new_file = other_dir.join("file.txt")
        new_file.write("")

        with watching(Path(watch_dir)) as (_, organizer_mock):
            new_file.move(watch_dir.join("file.txt"))

        organizer_mock.organize.assert_called_once_with(Path(watch_dir) / "file.txt")

    def test_OrganizerIsCalledWhenExistingDirectoryIsMovedIntoTheWatchDirectory(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        other_dir = tmpdir.mkdir("other")
        new_dir = other_dir.mkdir("dir")
        new_dir.join("file.txt").write("")

        with watching(Path(watch_dir)) as (_, organizer_mock):
            new_dir.move(watch_dir.join("dir"))

        organizer_mock.organize.assert_called_once_with(Path(watch_dir) / "dir")

    def test_OrganizerIsCalledWhenNewFileIsCreatedAfterChangingWatchDir(self, tmpdir):
        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.mkdir("watch2")

        with watching(Path(old_watch_dir)) as (watcher, organizer_mock):
            watcher.watch_dir = Path(new_watch_dir)
            new_watch_dir.join("file.txt").write("")

        organizer_mock.organize.assert_called_once_with(Path(new_watch_dir) / "file.txt")
        assert watcher.watch_dir == Path(new_watch_dir)

    def test_OrganizerIsNOTCalledWhenNewFileIsCreatedInOldDirectoryAfterChangingWatchDir(
            self, tmpdir):
        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.mkdir("watch2")

        with watching(Path(old_watch_dir)) as (watcher, organizer_mock):
            watcher.watch_dir = Path(new_watch_dir)
            old_watch_dir.join("file.txt").write("")

        organizer_mock.organize.assert_not_called()

    def test_ChangingToNonExistingWatchDirRaisesFileNotFoundAndKeepsWatchDir(self, tmpdir):
        old_watch_dir = tmpdir.mkdir("watch1")
        new_watch_dir = tmpdir.join("watch2")

        with watching(Path(old_watch_dir)) as (watcher, organizer_mock):
            with raises(OSError):
                watcher.watch_dir = Path(new_watch_dir)

            old_watch_dir.join("file.txt").write("")

        organizer_mock.organize.assert_called_once_with(Path(old_watch_dir) / "file.txt")
        assert watcher.watch_dir == Path(old_watch_dir)

    def test_OrganizerIsCalledWhenWatcherIsStartedAndWatchDirectoryContainsAFile(self, tmpdir):
        watch_dir = tmpdir.mkdir("watch")
        watch_dir.join("file.txt").write("")

        with watching(Path(watch_dir)) as (_, organizer_mock):
            pass

        organizer_mock.organize.assert_called_once_with(Path(watch_dir) / "file.txt")
