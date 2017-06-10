import pytest

from show_organizer.episode import Episode
from show_organizer.organizer import Organizer
from show_organizer.tvshow import TVShow


class TestOrganizer:

    # Using the same storage directory for all tests
    organizer = Organizer("STORAGE_DIR")

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

        assert self.organizer.episode_dir(episode) == expected_directory
