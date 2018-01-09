import logging
import os
import shutil
import threading

from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.storage_manager import StorageManager, StorageError
from episode_organizer.daemon.watch_handler import WatchHandler
from episode_organizer.daemon.watcher import Watcher


class Organizer(WatchHandler):
    """
    The organizer is the central component of the application. It talks to all other components and makes the
    application work. This is the entry point of the organizing service.
    """

    logger = logging.getLogger('organizer')

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

        self._watch_dir_lock = threading.Lock()
        self._storage_dir_lock = threading.Lock()

    @property
    def watch_dir(self):
        return self.watcher.watch_dir

    @property
    def storage_dir(self):
        return self.storage_manager.storage_dir

    def set_storage_dir(self, value):
        """
        Sets a new storage directory for the storage manager. If the directory does not exist, then it raises a 
        FileNotFoundError and directory is not changed.
        
        :param value: the path to the new storage directory. 
        :raises FileNotFoundError: if the directory does not exist.
        """
        with self._storage_dir_lock:
            self.storage_manager.storage_dir = value

    def start(self):
        """ Starts the organizing service """
        self.watcher.start()
        self.watcher.add_handler(self)

    def stop(self):
        """ Signals the organizing service to stop """
        self.watcher.stop()

    def join(self):
        """ Blocks until the organizing terminates """
        self.watcher.join()

    def set_watch_dir(self, watch_dir):
        """
        Sets the directory to look for new episode files. This method is thread safe

        :raises FileNotFoundError: if the given directory does not exist.
        """
        with self._watch_dir_lock:
            self.watcher.change_watch_dir(watch_dir)

    def on_new_directory(self, dir_path):
        """ Called by the watcher if the service is running when a new directory is detected in the watch directory """
        self.logger.info("Detected new directory: %s" % os.path.relpath(dir_path, self.watch_dir))
        self._handle_new_path(dir_path)

    def on_new_file(self, file_path):
        """ Called by the watcher if the service is running when a new file is detected in the watch directory """
        self.logger.info("Detected new file: %s" % os.path.relpath(file_path, self.watch_dir))
        self._handle_new_path(file_path)

    def _handle_new_path(self, path):
        """
        Handles a newly detected file or directory in the watch directory. It uses the filter to determine if there
        is a new episode file and if it there is, then it uses and the mapper and storage manager to store the
        episode in the correct sub-directory in the storage directory.
        """
        try:
            self.logger.info("Determining episode file...")
            episode_file = self.episode_filter.get_episode_file(path)
            self.logger.info("Determined episode file is '%s'" % os.path.relpath(episode_file, self.watch_dir))

            self.logger.info("Obtaining episode information...")
            episode = self.mapper.map_to_episode(os.path.basename(path))
            self.logger.info("Obtained info: %s" % str(episode))

            self.logger.info("Moving episode file to storage...")
            storage_path = self.storage_manager.store(episode_file, episode)
            self.logger.info("Episode stored in '%s'" % os.path.relpath(storage_path, self.storage_manager.storage_dir))

            if os.path.exists(path):
                shutil.rmtree(path)
                self.logger.info("Removed '%s' from watch directory" % os.path.relpath(path, self.watch_dir))

        except StorageError as error:
            self.logger.error(str(error))
            # Unrecoverable error - exit the service
            self.logger.info("Unrecoverable error: service will exit")
            self.stop()

        except FileExistsError as error:  # avoid collision with OS Error
            self.logger.warning(str(error))

        except OSError:
            self.logger.exception("Unexpected OS Error was raised")

        except ValueError as error:
            self.logger.warning(str(error))

