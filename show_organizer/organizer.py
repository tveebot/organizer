import os

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.storage_manager import StorageManager
from show_organizer.watch_handler import WatchHandler
from show_organizer.watcher import Watcher


class Organizer(WatchHandler):

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
        episode_file = self.episode_filter.get_episode_file(dir_path)
        episode = self.mapper.map_to_episode(os.path.basename(dir_path))
        self.storage_manager.store(episode_file, episode)

    def on_new_file(self, file_path):
        episode_file = self.episode_filter.get_episode_file(file_path)
        episode = self.mapper.map_to_episode(os.path.basename(file_path))
        self.storage_manager.store(episode_file, episode)
