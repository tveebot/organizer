import os

import pytest

from show_organizer.episode import Episode
from show_organizer.storage_manager import StorageManager
from show_organizer.tvshow import TVShow


class TestStorageManager:

    @pytest.fixture
    def storage_dir(self, tmpdir):
        return tmpdir.mkdir("STORAGE_DIR")

    @pytest.fixture
    def watch_dir(self, tmpdir):
        return tmpdir.mkdir("WATCH_DIR")

    @pytest.fixture
    def episode_file(self, watch_dir):
        episode_file = watch_dir.join("Prison.Break.S05E09.mkv")
        episode_file.write("")  # actually create the file
        return str(episode_file)

    def test_store_EpisodeDirectoryAlreadyExists_MoveTheFileThere(self, storage_dir, episode_file):
        storage_manager = StorageManager(str(storage_dir))
        storage_dir.mkdir("Prison Break").mkdir("Season 05")

        storage_manager.store(episode_file, Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(episode_file)

    def test_store_OnlyTVShowDirectoryExists_CreateSeasonDirectoryAnMoveTheFileThere(self, storage_dir, episode_file):
        storage_manager = StorageManager(str(storage_dir))
        storage_dir.mkdir("Prison Break")

        storage_manager.store(episode_file, Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(str(episode_file))

    def test_store_EpisodeDirectoryDoesNotExist_CreateItAndMoveTheFileThere(self, storage_dir, episode_file):
        storage_manager = StorageManager(str(storage_dir))

        storage_manager.store(str(episode_file), Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(str(episode_file))

    def test_store_FileAlreadyExistsOnDestinationDirectory_RaiseFileExistsError(self, storage_dir, episode_file):
        storage_manager = StorageManager(str(storage_dir))
        storage_dir.mkdir("Prison Break").mkdir("Season 05").join("Prison.Break.S05E09.mkv").write("")

        with pytest.raises(FileExistsError,
                           message="File 'Prison.Break.S05E09.mkv' already exists in 'Prison Break/Season 05/'"):
            storage_manager.store(str(episode_file), Episode(TVShow("Prison Break"), season=5, number=9))
