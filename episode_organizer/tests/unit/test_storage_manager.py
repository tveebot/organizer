import pytest

from episode_organizer.episode import Episode
from episode_organizer.storage_manager import StorageManager
from episode_organizer.tvshow import TVShow


class TestStorageManager:

    # Using the same storage directory for all tests
    storage_manager = StorageManager("STORAGE_DIR")

    @pytest.mark.parametrize("episode, expected_directory", [
        (
                Episode(TVShow("Prison Break"), season=5, number=9),
                "STORAGE_DIR/Prison Break/Season 05"
        ),
        (
                Episode(TVShow("Castle 2009"), season=8, number=22),
                "STORAGE_DIR/Castle 2009/Season 08"
        ),
    ])
    def test_episode_dir(self, episode, expected_directory):

        assert self.storage_manager.episode_dir(episode) == expected_directory
