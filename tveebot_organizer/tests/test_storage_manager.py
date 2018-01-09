from pathlib import Path

import pytest

from tveebot_organizer.dataclasses import TVShow, Episode
from tveebot_organizer.storage_manager import StorageManager, EpisodeExists


class TestStorageManagerEpisodeDir:
    # Using the same storage directory for all tests
    storage_manager = StorageManager(Path("library"))

    @pytest.mark.parametrize("episode, expected_directory", [
        (
                Episode(TVShow("Prison Break"), season=5, number=9),
                Path("library/Prison Break/Season 05")
        ),
        (
                Episode(TVShow("Castle 2009"), season=8, number=22),
                Path("library/Castle 2009/Season 08")
        ),
        (
                Episode(TVShow("Castle 2009"), season=8, number=122),
                Path("library/Castle 2009/Season 08")
        ),
        (
                Episode(TVShow("Castle 2009"), season=18, number=122),
                Path("library/Castle 2009/Season 18")
        ),
        (
                Episode(TVShow("Castle 2009"), season=108, number=122),
                Path("library/Castle 2009/Season 108")
        ),
    ])
    def test_episode_dir(self, episode: Episode, expected_directory: Path):
        assert expected_directory == self.storage_manager.episode_dir(episode)


class TestStorageManagerStore:

    @pytest.fixture
    def storage_dir(self, tmpdir):
        return tmpdir.mkdir("STORAGE_DIR")

    @pytest.fixture
    def watch_dir(self, tmpdir):
        return tmpdir.mkdir("WATCH_DIR")

    @pytest.fixture
    def episode_file(self, watch_dir) -> Path:
        episode_file = watch_dir.join("Prison.Break.S05E09.mkv")
        episode_file.write("")  # actually create the file
        return Path(episode_file)

    EPISODE = Episode(TVShow("Prison Break"), season=5, number=9)

    def test_EpisodeDirectoryExists_FileIsMovedThere(self, storage_dir, episode_file):
        storage_dir.mkdir("Prison Break").mkdir("Season 05")
        storage_manager = StorageManager(Path(storage_dir))

        storage_manager.store(self.EPISODE, episode_file)

        episode_dst_path = storage_dir / "Prison Break" / "Season 05" / "Prison.Break.S05E09.mkv"
        assert episode_dst_path.exists()
        assert not episode_file.exists()

    def test_OnlyTVShowDirectoryExists_CreatesNecessaryDirectories(self, storage_dir, episode_file):
        storage_dir.mkdir("Prison Break")
        storage_manager = StorageManager(Path(storage_dir))

        storage_manager.store(self.EPISODE, episode_file)

        episode_dst_path = storage_dir / "Prison Break" / "Season 05" / "Prison.Break.S05E09.mkv"
        assert episode_dst_path.exists()
        assert not episode_file.exists()

    def test_TVShowDirectoryDoesNotExist_CreatesAllDirectories(self, storage_dir, episode_file):
        storage_manager = StorageManager(Path(storage_dir))

        storage_manager.store(self.EPISODE, episode_file)

        episode_dst_path = storage_dir / "Prison Break" / "Season 05" / "Prison.Break.S05E09.mkv"
        assert episode_dst_path.exists()
        assert not episode_file.exists()

    def test_LibraryAlreadyIncludesEpisode_RaisesEpisodeExistsAndKeepsFile(
            self, storage_dir, episode_file):
        storage_dir.mkdir("Prison Break") \
            .mkdir("Season 05") \
            .join("Prison.Break.S05E09.mkv") \
            .write("")
        storage_manager = StorageManager(Path(storage_dir))

        with pytest.raises(EpisodeExists):
            storage_manager.store(self.EPISODE, episode_file)

        assert episode_file.exists()

    def test_LibraryDirectoryDoesNotExist_RaisesFileNotFoundErrorAndKeepsFile(
            self, tmpdir, episode_file):
        storage_dir = tmpdir.join("STORAGE")
        storage_manager = StorageManager(Path(storage_dir))

        with pytest.raises(FileNotFoundError):
            storage_manager.store(self.EPISODE, episode_file)

        assert episode_file.exists()
