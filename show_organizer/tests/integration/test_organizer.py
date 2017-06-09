import os

import pytest

from show_organizer.episode import Episode
from show_organizer.organizer import Organizer
from show_organizer.tvshow import TVShow


class TestOrganizer:

    def test_store_EpisodeDirectoryDoesNotExist_CreateItAndMoveTheFileThere(self, tmpdir):
        storage_dir = tmpdir.mkdir("STORAGE_DIR")
        organizer = Organizer(str(storage_dir))

        watch_dir = tmpdir.mkdir("WATCH_DIR")
        video_file = watch_dir.join("Prison.Break.S05E09.720p.mkv")
        video_file.write("")  # actually create the file
        episode = Episode(TVShow("Prison Break"), season=5, number=9)

        organizer.store(str(video_file), episode)

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.720p.mkv"))
        assert not os.path.exists(str(video_file))
