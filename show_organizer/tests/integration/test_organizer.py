import os

import pytest

from show_organizer.episode import Episode
from show_organizer.organizer import Organizer
from show_organizer.tvshow import TVShow


class TestOrganizer:

    @pytest.fixture
    def storage_dir(self, tmpdir):
        return tmpdir.mkdir("STORAGE_DIR")

    @pytest.fixture
    def watch_dir(self, tmpdir):
        return tmpdir.mkdir("WATCH_DIR")

    @pytest.fixture
    def video_file(self, watch_dir):
        video_file = watch_dir.join("Prison.Break.S05E09.mkv")
        video_file.write("")  # actually create the file
        return str(video_file)

    def test_store_EpisodeDirectoryAlreadyExists_MoveTheFileThere(self, storage_dir, video_file):
        organizer = Organizer(str(storage_dir))
        storage_dir.mkdir("Prison Break").mkdir("Season 05")

        organizer.store(video_file, Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(video_file)

    def test_store_OnlyTVShowDirectoryExists_CreateSeasonDirectoryAnMoveTheFileThere(self, storage_dir, video_file):
        organizer = Organizer(str(storage_dir))
        storage_dir.mkdir("Prison Break")

        organizer.store(video_file, Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(str(video_file))

    def test_store_EpisodeDirectoryDoesNotExist_CreateItAndMoveTheFileThere(self, storage_dir, video_file):
        organizer = Organizer(str(storage_dir))

        organizer.store(str(video_file), Episode(TVShow("Prison Break"), season=5, number=9))

        assert os.path.exists(os.path.join(str(storage_dir), "Prison Break/Season 05/Prison.Break.S05E09.mkv"))
        assert not os.path.exists(str(video_file))

    def test_store_FileAlreadyExistsOnDestinationDirectory_RaiseFileExistsError(self, storage_dir, video_file):
        organizer = Organizer(str(storage_dir))
        storage_dir.mkdir("Prison Break").mkdir("Season 05").join("Prison.Break.S05E09.mkv").write("")

        with pytest.raises(FileExistsError,
                           message="File 'Prison.Break.S05E09.mkv' already exists in 'Prison Break/Season 05/'"):
            organizer.store(str(video_file), Episode(TVShow("Prison Break"), season=5, number=9))
