import pytest

from show_organizer.filter import Filter


class TestFilter:

    @pytest.mark.parametrize("video_path", [
        "video.mkv",
        "video.mp4",
        "video.avi",
        "video.m4p",
        "video.m4v",
        "video.MKV",
        "video.mKV",
    ])
    def test_is_video_file(self, video_path, tmpdir):
        path = tmpdir.join(video_path)
        path.write("")

        assert Filter.is_video_file(str(path))

    @pytest.mark.parametrize("video_path", [
        "video.txt",
        "video.mp3",
        "video.md",
        "video",
    ])
    def test_is_video_file_IsNotVideoFile(self, video_path, tmpdir):
        path = tmpdir.join(video_path)
        path.write("")

        assert not Filter.is_video_file(str(path))

    def test_is_video_file_PathIsADirectory_NotVideoFile(self, tmpdir):
        path = tmpdir.mkdir("video.mkv")

        assert not Filter.is_video_file(str(path))

    def test_is_video_file_PathDoesNotExist_NotVideoFile(self, tmpdir):
        path = tmpdir.join("video.mkv")  # without calling write() the file is not created

        assert not Filter.is_video_file(str(path))

    def test_get_episode_file_PathToVideoFile_ReturnThatSameVideoFile(self, tmpdir):
        episode_filter = Filter()

        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert episode_filter.get_episode_file(path=str(video_file)) == str(video_file)

    def test_get_episode_file_PathToDirectoryWithASingleVideoFile_ReturnTheSingleVideoFile(self, tmpdir):
        episode_filter = Filter()

        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert episode_filter.get_episode_file(path=str(tmpdir)) == video_file

    def test_get_episode_file_PathToDirectoryWithASingleVideoFileAndOtherFiles_ReturnTheVideoFile(self, tmpdir):
        episode_filter = Filter()

        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        video_file = tmpdir.join("video.mkv")
        video_file.write("")

        assert episode_filter.get_episode_file(path=str(tmpdir)) == video_file

    def test_get_episode_file_PathToDirectoryWithTwoVideoFiles_ReturnTheBiggestFile(self, tmpdir):
        episode_filter = Filter()

        # Note the small file has only 4 characters and the big file has 13 characters

        tmpdir.join("small_video.mkv").write("small")
        big_video_file = tmpdir.join("big_video.mkv")
        big_video_file.write("VERY BIG FILE")

        assert episode_filter.get_episode_file(path=str(tmpdir)) == big_video_file

    def test_get_episode_file_PathToEmptyDirectory_RaisesValueError(self, tmpdir):
        episode_filter = Filter()

        with pytest.raises(ValueError, message="The directory '%s' does not contain any video file" % str(tmpdir)):
            episode_filter.get_episode_file(path=str(tmpdir))

    def test_get_episode_file_PathToDirectoryWithFilesButNoneIsAVideoFile_RaisesValueError(self, tmpdir):
        episode_filter = Filter()

        tmpdir.join("other.txt").write("this is a text file")
        tmpdir.join("other.mp3").write("this is a music file")
        tmpdir.mkdir("directory.mp4")

        with pytest.raises(ValueError, message="The directory '%s' does not contain any video file" % str(tmpdir)):
            episode_filter.get_episode_file(path=str(tmpdir))

    def test_get_episode_file_PathToNonVideoFile_RaisesValueError(self, tmpdir):
        episode_filter = Filter()

        video_file = tmpdir.join("file.txt")
        video_file.write("")

        with pytest.raises(ValueError, message="The path '%s' is not a video file" % str(video_file)):
            episode_filter.get_episode_file(path=str(video_file))
