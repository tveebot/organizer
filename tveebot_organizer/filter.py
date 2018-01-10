from pathlib import Path
from typing import Optional


class Filter:
    """
    The filter is one of the sub-components of the *Organizer*. An organizer is associated with a
    single filter. The organizer relies on the filter to filter out files that do not correspond
    to episode files. Thus, it calls the filter every time is starts to organize something.

    The filter includes a single method *find_episode_file()* which takes a path. This method is
    able to handle both files and directories. If the input is a directory, it looks for the
    episode file inside that directory and ignores all other files.
    """

    # Supported video file extensions
    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def find_episode_file(self, path: Path) -> Optional[Path]:
        """
        Finds the episode file corresponding to the given *path* and returns it.

        The 'path' argument may be a file or a directory.

        If *path* is a file, then it assumes this file must be the episode file.
        If *path* is a directory, then it looks for the largest video file inside the directory
        and considers that to be the episode file.

        If the episode file does not correspond to a video file, then it returns None. Returning
        None indicates the filter was not able to find an episode file for the given *path*.

        :raise: ValueError: if *path* is neither a file or a directory
        """
        if path.is_file():
            if self.is_video_file(path):
                episode_file = path
            else:
                episode_file = None

        elif path.is_dir():
            try:
                # Look for the biggest video file inside the directory
                episode_file = max([file for file in path.iterdir() if self.is_video_file(file)],
                                   key=lambda p: p.stat().st_size)
            except ValueError:
                # The directory is empty
                episode_file = None

        else:
            raise ValueError(f"path '{path}' is neither a file or a directory")

        return episode_file

    @staticmethod
    def is_video_file(path: Path) -> bool:
        """
        Determines whether not *path* corresponds to a video file or not.

        :return: True if *path* is a video file and False if otherwise.
        """
        return path.is_file() and path.suffix.lower() in Filter.video_extensions
