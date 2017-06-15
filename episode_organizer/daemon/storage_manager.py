import logging
import os
import shutil

from episode_organizer.episode import Episode


class StorageError(Exception):
    """
    Raised to indicate there is a critical error with the storage and the application can not proceed. This exception
    is raised when, for instance, the storage directory is deleted.
    """
    pass


class StorageManager:
    """
    The storage manager is one of the most important components. Its job is to 'store' (see store method) the episode
    file in the correct sub-directory inside the storage directory. The directory where the file is stored is determined
    based on the episode information included alongside with the episode file.
    """

    logger = logging.getLogger('storageManager')

    def __init__(self, storage_dir: str):
        """ Defines the storage directory. This directory is the entry point where all tv show episode is stored. """
        self._storage_dir = storage_dir
        self.logger.info("Storage directory: %s" % self.storage_dir)

    @property
    def storage_dir(self):
        return self._storage_dir

    @storage_dir.setter
    def storage_dir(self, value):

        if not os.path.isdir(value):
            raise FileNotFoundError("New storage directory does not exist: %s" % value)

        self._storage_dir = value

    def store(self, episode_file: str, episode: Episode):
        """
        This is the entry point of the storage manager. This method is called to store an episode file in it correct
        place, based on its episode information provided in the 'episode' argument. If the destination directory does
        not exist, then it is automatically created. The episode file is moved to the destination directory and not
        copied. Which means that after calling this method the file is removed from its current directory.

        :param episode_file: the episode file to store.
        :param episode:      the episode information corresponding to the given episode file.
        :raise FileExistsError: if the episode file already exists in the destination directory.
        """
        move_dir = self.episode_dir(episode)
        self.logger.debug("Episode file will be stored in directory: %s" % os.path.relpath(self.storage_dir, move_dir))

        if not os.path.isdir(self.storage_dir):
            raise StorageError("Storage directory was deleted")

        # Make sure the directory exists
        self.logger.debug("Creating directories for the episode file")
        os.makedirs(move_dir, exist_ok=True)

        try:
            # Only then, move the file to the directory
            self.logger.debug("Moving episode file to '%s'" % move_dir)
            shutil.move(episode_file, move_dir)

        except shutil.Error:
            raise FileExistsError("File '%s' already exists in '%s'" %
                                  (os.path.basename(episode_file), os.path.relpath(move_dir, start=self.storage_dir)))

    def episode_dir(self, episode: Episode):
        """
        Determines the episode directory based on its information. In its current form, the directory of an episode
        is composed of a season folder of the form 'Season XX', where XX indicates the season number to which the
        episode belongs. This directory is included inside a tv show directory with its name. For example, an episode
        from season 1 of a tv show called 'Example' is stored in 'Example/Season 01'.

        :param episode: the episode information.
        :return: the path to the directory where the episode should be stored.
        """
        return os.path.join(self.storage_dir, episode.tvshow.name, "Season %02d" % episode.season)