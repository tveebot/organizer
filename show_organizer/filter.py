import os


class Filter:
    """
    The filter is an important component. The filter is called every time a new file or directory is detected by the
    watcher. Its job is to filter out irrelevant files and select only the single episode file. For a new directory,
    the filter looks for video files inside the directory and determines the episode directory to be the largest of
    those.
    """

    # Supported video file extensions
    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def get_episode_file(self, path):
        """
        Entry point for the filter. The 'path' argument may be a file or a directory. If it is a file and this file
        is a video file, then that file is returned. If 'path' is a directory, then the episode file corresponds to
        the biggest video file inside that directory.

        :param path: the path to a file or directory.
        :return: the episode file.
        :raise ValueError: if the path is a file and it is not a video file or if path is a directory and does not
                           contain any video file.
        """

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
    def is_video_file(path):
        """
        Checks is a file is a video file or not. To determine this, the method checks if 'path' is an existing
        file and if its extension is corresponds to a video extension (see supported video extensions above).

        :param path: the path to check if is a video file.
        :return: True if the path is a video file and False if otherwise.
        """
        if not os.path.isfile(path):
            return False

        path, extension = os.path.splitext(path)
        return extension.lower() in Filter.video_extensions

    @staticmethod
    def _list_video_files(directory):
        """
        Iterator over the video files inside a directory.

        :param directory: directory to iterate over.
        :return: each video file inside the given directory
        """
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if Filter.is_video_file(file_path):
                yield file_path
