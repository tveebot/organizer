import os


def __list_video_files():
    for file in os.listdir(path):
        __


class Filter:

    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def get_episode_file(self, path):

        if os.path.isdir(path):

            # Look inside the directory for the biggest video file
            episode_file = max((file for file in self._list_video_files(path)), key=os.path.getsize)

            if episode_file is None:
                raise ValueError("The directory '%s' does not contain any video file" % path)

            return episode_file

        elif os.path.isfile(path) and self.is_video_file(path):
            return path

        else:
            raise ValueError("The path '%s' is not a video file" % path)

    @staticmethod
    def is_video_file(file_path):

        if not os.path.isfile(file_path):
            return False

        path, extension = os.path.splitext(file_path)

        return extension.lower() in Filter.video_extensions

    @staticmethod
    def _list_video_files(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if Filter.is_video_file(file_path):
                yield file_path
