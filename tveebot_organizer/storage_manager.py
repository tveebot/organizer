import logging
import shutil
from pathlib import Path

from tveebot_organizer.dataclasses import Episode


class EpisodeExists(Exception):
    pass


logger = logging.getLogger('storageManager')


class StorageManager:
    """
    The storage manager is one of the sub-components of the *Organizer*. An organizer is associated
    with a single storage manager. The storage manager is responsible for storing the episode files
    in the library according to some pre-defined organization structure.
    """

    def __init__(self, library_dir: Path):
        """ Initializes the storage manager, specifying the library directory. """
        self._library_dir = library_dir

    @property
    def library_dir(self) -> Path:
        return self._library_dir

    @library_dir.setter
    def library_dir(self, directory: Path):
        if not directory.is_dir():
            raise FileNotFoundError("library directory was not found: %s" % directory)

        self._library_dir = directory

    def store(self, episode: Episode, path: Path):
        """
        Stores an *episode* in the library.

        The episode file in *path* is **moved** to the library, which means it will be removed from
        its current location.

        :param episode:           the episode to be stored
        :param path:              the path to the episode file corresponding to *episode*
        :raise EpisodeExists:     if the library already includes this episode
        :raise FileNotFoundError: if the library directory does not exist
        :raise OSError:           if some error occurs while trying to store the episode
        """
        episode_dir = self.episode_dir(episode)
        logger.debug("episode will be stored in: %s" % episode_dir.relative_to(self.library_dir))

        if not self.library_dir.is_dir():
            raise FileNotFoundError("library directory was removed: %s" % self.library_dir)

        # Create the directory to store the episode
        episode_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.debug("moving episode to '%s'" % episode_dir.relative_to(self.library_dir))
            shutil.move(src=str(path), dst=str(episode_dir))
        except shutil.Error:
            # Destination path already exists
            raise EpisodeExists("library already includes episode")

    def episode_dir(self, episode: Episode) -> Path:
        """
        Determines the episode directory based on its information.

        In its current form, the directory of an episode is composed of a season folder of the
        form 'Season XX', where XX indicates the season number to which the episode belongs. This
        directory is included inside a tv show directory with its name. For example, an episode
        from season 1 of a tv show called 'Example' is stored in 'Example/Season 01'.

        :param episode: the episode information.
        :return: the path to the directory where the episode should be stored.
        """
        return self.library_dir / episode.tvshow.name / ("Season %02d" % episode.season)
