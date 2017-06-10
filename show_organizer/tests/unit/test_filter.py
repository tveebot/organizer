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
