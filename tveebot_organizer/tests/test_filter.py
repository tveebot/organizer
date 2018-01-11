import pytest
from hamcrest import *

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

        episode_files = Filter().filter(path_from(video_file))

        assert_that(episode_files, has_items(path_from(video_file)))

    def test_GivenANonVideoFileReturnsAnEmptyList(self, tmpdir):
        video_file = tmpdir.join("video.txt")
        video_file.write("")

        episode_files = Filter().filter(path_from(video_file))

        assert_that(episode_files, is_(empty()))

    def test_GivenADirectoryWithASingleVideoFileReturnsThatFile(self, tmpdir):
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, has_items(path_from(video_file)))

    def test_GivenADirectoryWithOneVideoFileAndOtherNonVideoFilesReturnsTheVideoFile(self, tmpdir):
        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, has_items(path_from(video_file)))

    def test_GivenADirectoryWithTwoVideoFilesReturnsBothFiles(self, tmpdir):
        file1 = tmpdir.join("video1.mkv")
        file2 = tmpdir.join("video2.mkv")
        file1.write("")
        file2.write("")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, has_items(path_from(file1), path_from(file2)))

    def test_GivenADirectoryWithTwoVideoFilesWithDifferentExtensionsReturnsBothFiles(self, tmpdir):
        file1 = tmpdir.join("video1.mkv")
        file2 = tmpdir.join("video2.avi")
        file1.write("")
        file2.write("")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, has_items(path_from(file1), path_from(file2)))

    def test_GivenAnEmptyDirectoryReturnsAnEmptyList(self, tmpdir):
        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, is_(empty()))

    def test_GivenADirectoryWithNoVideoFilesReturnsAnEmptyList(self, tmpdir):
        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        tmpdir.mkdir("directory.mp4")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, is_(empty()))

    def test_GivenADirectoryWithMultipleVideoFilesInSubDirectoriesReturnsAllVideoFiles(
            self, tmpdir):
        subdir1 = tmpdir.mkdir("dir1")
        subdir2 = tmpdir.mkdir("dir2")
        file1 = subdir1.join("video1.mkv")
        file2 = tmpdir.join("video2.mkv")
        file3 = subdir2.join("video3.avi")
        file1.write("")
        file2.write("")
        file3.write("")

        episode_files = Filter().filter(path_from(tmpdir))

        assert_that(episode_files, has_items(path_from(file1), path_from(file2), path_from(file3)))
