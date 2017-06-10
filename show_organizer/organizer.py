import os
import shutil

from show_organizer.episode import Episode


class Organizer:
    """
    The organizer is one of the most important components. Its job is to 'store' (see store method) the episode file in
    the correct sub-directory inside the storage directory. The directory where the file is stored is determined
    based on the episode information included alongside with the episode file.
    """

    def __init__(self, storage_dir: str):
        """ Defines the storage directory. This directory is the entry point where all tv show episode is stored. """
        self.storage_dir = storage_dir

    def store(self, episode_file: str, episode: Episode):
        """
        This is the entry point of the organizer. This method is called to store an episode file in it correct place,
        based on its episode information provided in the 'episode' argument. If the destination directory does not
        exist, then it is automatically created. The episode file is moved to the destination directory and not
        copied. Which means that after calling this method the file is removed from its current directory.

        :param episode_file: the episode file to store.
        :param episode:      the episode information corresponding to the given episode file.
        :raise FileExistsError: if the episode file already exists in the destination directory.
        """
        move_dir = self.get_episode_directory(episode)

        # Make sure the directory exists
        os.makedirs(move_dir, exist_ok=True)

        try:
            # Only then, move the file to the directory
            shutil.move(episode_file, move_dir)

        except shutil.Error:
            raise FileExistsError("File '%s' already exists in '%s'" %
                                  (os.path.basename(episode_file), os.path.relpath(move_dir, start=self.storage_dir)))

    def get_episode_directory(self, episode: Episode):
        """
        Determines the episode directory based on its information. In its current form, the directory of an episode
        is composed of a season folder of the form 'Season XX', where XX indicates the season number to which the
        episode belongs. This directory is included inside a tv show directory with its name. For example, an episode
        from season 1 of a tv show called 'Example' is stored in 'Example/Season 01'.

        :param episode: the episode information.
        :return: the path to the directory where the episode should be stored.
        """
        return os.path.join(self.storage_dir, episode.tvshow.name, "Season %02d" % episode.season)
