import os

import logging

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.storage_manager import StorageManager, StorageError
from show_organizer.watch_handler import WatchHandler
from show_organizer.watcher import Watcher


class Organizer(WatchHandler):

    logger = logging.getLogger('show_organizer.Organizer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    def __init__(self, watch_dir: str, episode_filter: Filter, mapper: Mapper, storage_manager: StorageManager):
        """
        Initializes the organizer. It takes all necessary components to setup the service.

        :param watch_dir:       the directory to watch for new episode files.
        :param episode_filter:  the filter to select a episode files.
        :param mapper:          the mapper used to map episode files to their information.
        :param storage_manager: component responsible for managing the storage of new episode files.
        """
        super().__init__()
        self.watcher = Watcher(watch_dir)
        self.episode_filter = episode_filter
        self.mapper = mapper
        self.storage_manager = storage_manager

    def start(self):
        self.watcher.start()
        self.watcher.add_handler(self)

    def stop(self):
        self.watcher.stop()

    def on_new_directory(self, dir_path):
        self._handle_new_path(dir_path)

    def on_new_file(self, file_path):
        self._handle_new_path(file_path)

    def _handle_new_path(self, path):

        try:
            self.logger.info("Obtaining episode file from '%s'" % path)
            episode_file = self.episode_filter.get_episode_file(path)
            self.logger.info("Filter indicated the episode file is '%s'" % path)

            self.logger.info("Obtaining episode information")
            episode = self.mapper.map_to_episode(os.path.basename(path))
            self.logger.info("Obtained info: %s" % str(episode))

            self.logger.info("Moving episode file to storage")
            self.storage_manager.store(episode_file, episode)
            self.logger.info("Episode file was moved to storage")

        except StorageError as error:
            self.logger.error(str(error))

        except OSError:
            self.logger.exception("Unexpected OS Error was raised")

        except ValueError as error:
            self.logger.error(str(error))

