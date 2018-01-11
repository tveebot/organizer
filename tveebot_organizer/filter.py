from pathlib import Path
from typing import Optional, List


class Filter:
    """
    The filter is one of the sub-components of the *Organizer*. An organizer is associated with a
    single filter. The organizer relies on the filter to filter out files that do not correspond
    to episode files. Thus, it calls the filter every time is starts to organize something.

    The filter includes a single method *filter()* which takes a path. This method is able to
    handle both files and directories. If the input is a directory, it looks for all files
    recursively and filters out those that cannot correspond to episode files.
    """

    # Supported video file extensions
    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def filter(self, path: Path) -> List[Path]:
        """
        Filters all files corresponding to the given *path*, selecting only those that might
        correspond to episode files.

        The 'path' argument may be a file or a directory.

        If *path* is a video file, then it assumes this file must be the episode file. If *path*
        is a directory, then it looks for video files inside the directory and returns only those.

        This method returns a list of paths to the video files found for the given *path*. It
        returns an empty list if it does not find any video file.

        :raise: ValueError: if *path* is neither a file or a directory
        """
        video_files = []
        if path.is_file():
            if self.is_video_file(path):
                video_files = [path]

        elif path.is_dir():

            # Look for video files in this directory an all sub-directories, recursively
            video_files = []  # holds all video files found
            directories = [path]  # keeps track of directories left to explore
            while len(directories) > 0:
                directory = directories.pop()
                for item in directory.iterdir():
                    if item.is_dir():
                        directories.append(item)
                    elif self.is_video_file(item):
                        video_files.append(item)

        else:
            raise ValueError("path '%s' is neither a file or a directory" % path)

        return video_files

    @staticmethod
    def is_video_file(path: Path) -> bool:
        """
        Determines whether or not *path* corresponds to a video file or not.

        :return: True if *path* is a video file and False if otherwise.
        """
        return path.is_file() and path.suffix.lower() in Filter.video_extensions
