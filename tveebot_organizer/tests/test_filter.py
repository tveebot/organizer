import pytest

from tveebot_organizer.filter import Filter
from tveebot_organizer.tests.utils import path_from


class TestFilterIsVideoFile:

    @pytest.mark.parametrize("video_path", [
        "video.mkv",
        "video.mp4",
        "video.avi",
        "video.m4p",
        "video.m4v",
        "video.MKV",
        "video.mKV",
    ])
    def test_ExistingVideoFilesAreActuallyVideoFiles(self, video_path, tmpdir):
        path = tmpdir.join(video_path)
        path.write("")

        assert Filter.is_video_file(path_from(path))

    @pytest.mark.parametrize("video_path", [
        "video.txt",
        "video.mp3",
        "video.md",
        "video",
    ])
    def test_ExistingNonVideoFilesAreNotVideoFiles(self, video_path, tmpdir):
        path = tmpdir.join(video_path)
        path.write("")

        assert not Filter.is_video_file(path_from(path))

    def test_PathToDirectoryWithVideoExtensionIsNotAVideoFile(self, tmpdir):
        path = tmpdir.mkdir("video.mkv")

        assert not Filter.is_video_file(path_from(path))

    def test_NonExistingPathIsNotAVideoFile(self, tmpdir):
        path = tmpdir.join("video.mkv")

        assert not Filter.is_video_file(path_from(path))


class TestFilterFindEpisodeFile:

    def test_GivenAVideoFileReturnsThatFile(self, tmpdir):
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert Filter().filter(path_from(video_file)) == path_from(video_file)

    def test_GivenANonVideoFileReturnsNone(self, tmpdir):
        video_file = tmpdir.join("video.txt")
        video_file.write("")

        assert Filter().filter(path_from(video_file)) is None

    def test_GivenADirectoryWithASingleVideoFileReturnsThatFile(self, tmpdir):
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert Filter().filter(path_from(tmpdir)) == path_from(video_file)

    def test_GivenADirectoryWithOneVideoFileAndOtherNonVideoFilesReturnsTheVideoFile(self, tmpdir):
        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert Filter().filter(path_from(tmpdir)) == path_from(video_file)

    def test_GivenADirectoryWithTwoVideoFilesReturnsTheBiggestFile(self, tmpdir):
        # Note the small file has only 4 characters and the big file has 13 characters

        tmpdir.join("small_video.mkv").write("small")
        big_video_file = tmpdir.join("big_video.mkv")
        big_video_file.write("VERY BIG FILE")

        assert Filter().filter(path_from(tmpdir)) == big_video_file

    def test_GivenAnEmptyDirectoryReturnsNone(self, tmpdir):
        assert Filter().filter(path_from(tmpdir)) is None

    def test_GivenADirectoryWithNoVideoFilesReturnsNone(self, tmpdir):
        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        tmpdir.mkdir("directory.mp4")

        assert Filter().filter(path_from(tmpdir)) is None
