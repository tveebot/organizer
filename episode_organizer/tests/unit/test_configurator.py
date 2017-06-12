import pytest

from episode_organizer.configurator import Configurator
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


class TestConfigurator:

    def test_SetWatchDirToExistingDir_WatchDirWasSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        new_watch_dir = tmpdir.mkdir("new_watch")
        # noinspection PyTypeChecker
        configurator = Configurator(Organizer(str(watch_dir), None, None, None))

        configurator.set_watch_dir(str(new_watch_dir))

        assert configurator.watch_dir() == str(new_watch_dir)

    def test_SetWatchDirToNonExistingDir_RaiseFileNotFoundAndKeepsWatchDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        new_watch_dir = tmpdir.join("new_watch")
        # noinspection PyTypeChecker
        configurator = Configurator(Organizer(str(watch_dir), None, None, None))

        with pytest.raises(FileNotFoundError):
            configurator.set_watch_dir(str(new_watch_dir))

        assert configurator.watch_dir() == str(watch_dir)

    def test_SetStorageDirToExistingDir_StorageDirWasSetToNewDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.mkdir("new_storage")
        # noinspection PyTypeChecker
        configurator = Configurator(Organizer(str(watch_dir), None, None, StorageManager(str(storage_dir))))

        configurator.set_storage_dir(str(new_storage_dir))

        assert configurator.storage_dir() == str(new_storage_dir)

    def test_SetStorageDirToNonExistingDir_RaiseFileNotFoundAndKeepsStorageDir(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")
        new_storage_dir = tmpdir.join("new_storage")
        # noinspection PyTypeChecker
        configurator = Configurator(Organizer(str(watch_dir), None, None, StorageManager(str(storage_dir))))

        with pytest.raises(FileNotFoundError):
            configurator.set_storage_dir(str(new_storage_dir))

        assert configurator.storage_dir() == str(storage_dir)
