from time import sleep

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.organizer import Organizer
from show_organizer.storage_manager import StorageManager


class TestOrganizer:

    def test_organize_DownloadedAnEpisodeFile(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        organizer.start()

        # New episode file was downloaded
        watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").write("")

        sleep(1)

        organizer.stop()

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()

    def test_organize_DownloadEpisodeInsideADirectory(self, tmpdir):

        watch_dir = tmpdir.mkdir("watch")
        storage_dir = tmpdir.mkdir("storage")

        organizer = Organizer(str(watch_dir), Filter(), Mapper(), StorageManager(str(storage_dir)))
        organizer.start()

        # New episode file was downloaded
        other_dir = tmpdir.mkdir("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]")
        episode_file = other_dir.join("Prison.Break.S05E09.720p.HDTV.x264.mkv")
        episode_file.write("")
        other_dir.move(watch_dir.join("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]"))

        sleep(1)

        organizer.stop()

        # Check the file was moved to the correct storage directory
        assert storage_dir.join("Prison Break").join("Season 05").join("Prison.Break.S05E09.720p.HDTV.x264.mkv").check()
        assert not other_dir.check()

    # TODO file already exists in destination directory
    # TODO no permission or OS error
