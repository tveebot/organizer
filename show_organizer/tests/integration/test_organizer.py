import os

import pytest

from show_organizer.episode import Episode
from show_organizer.organizer import Organizer
from show_organizer.tvshow import TVShow


class TestOrganizer:

    def test_store_EpisodeDirectoryAlreadyExists_MoveTheFileThere(self, tmpdir):
        storage_dir = tmpdir.mkdir("STORAGE_DIR")
        organizer = Organizer(str(storage_dir))

        watch_dir = tmpdir.mkdir("WATCH_DIR")
        watch_dir.mkdir("Prison Break").mkdir("Season 05")
        video_file = watch_dir.join("Prison.Break.S05E09.720p.mkv")
        video_file.write("")  # actually create the file

        organizer.store(str(video_file), Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.720p.mkv"))
        assert not os.path.exists(str(video_file))

    def test_store_OnlyTVShowDirectoryExists_CreateSeasonDirectoryAnMoveTheFileThere(self, tmpdir):
        storage_dir = tmpdir.mkdir("STORAGE_DIR")
        organizer = Organizer(str(storage_dir))

        watch_dir = tmpdir.mkdir("WATCH_DIR")
        watch_dir.mkdir("Prison Break")
        video_file = watch_dir.join("Prison.Break.S05E09.720p.mkv")
        video_file.write("")  # actually create the file

        organizer.store(str(video_file), Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.720p.mkv"))
        assert not os.path.exists(str(video_file))

    def test_store_EpisodeDirectoryDoesNotExist_CreateItAndMoveTheFileThere(self, tmpdir):
        storage_dir = tmpdir.mkdir("STORAGE_DIR")
        organizer = Organizer(str(storage_dir))

        watch_dir = tmpdir.mkdir("WATCH_DIR")
        video_file = watch_dir.join("Prison.Break.S05E09.720p.mkv")
        video_file.write("")  # actually create the file

        organizer.store(str(video_file), Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.720p.mkv"))
        assert not os.path.exists(str(video_file))
