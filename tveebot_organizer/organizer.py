import logging
import shutil
from pathlib import Path

from tveebot_organizer.filter import Filter
from tveebot_organizer.matcher import Matcher
from tveebot_organizer.storage_manager import StorageManager, EpisodeExists

logger = logging.getLogger('organizer')


class Organizer:
    """
    The organizer is the central component of the application.
    """

    def __init__(self, filter: Filter, matcher: Matcher, storage_manager: StorageManager):
        """
        Initializes the organizer. It takes all necessary components to setup the service.
        """
        super().__init__()
        self.filter = filter
        self.matcher = matcher
        self.storage_manager = storage_manager

    def organize(self, path: Path):
        """
        Organizes one episode.

        Takes a *path* to a file or a directory, matches with an episode, and stores it in a
        library.
        """
        logger.debug("looking for episode file...")
        episode_file = self.filter.filter(path)

        if episode_file is None:
            logger.info("ignored '%s'" % path.name)
            return

        logger.info("episode file is '%s'" % episode_file.name)

        try:
            logger.debug("matching episode...")
            episode = self.matcher.match(path.name)
            logger.info("episode matched to %s" % str(episode))
        except ValueError:
            logger.warning("ignored '%s': could not match it to an episode" % path.name)
            return

        try:
            logger.debug("storing episode...")
            self.storage_manager.store(episode, episode_file)

            episode_dir = self.storage_manager.episode_dir(episode) \
                .relative_to(self.storage_manager.library_dir)
            logger.info("stored episode to %s" % episode_dir)

        except EpisodeExists as error:
            logger.warning(str(error))
        except FileNotFoundError as error:
            logger.error(str(error))
        except OSError as error:
            logger.error("got unexpected error: %s" % str(error))
        else:
            if path.exists():
                shutil.rmtree(str(path))
                logger.info("cleared '%s' from watch directory" % path.name)
