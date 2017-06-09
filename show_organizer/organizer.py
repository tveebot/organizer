import os

from show_organizer.episode import Episode


class Organizer:

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir

    def get_episode_directory(self, episode: Episode):
        return os.path.join(self.storage_dir, episode.tvshow.name, "Season %02d" % episode.season)

    def store(self, video_file: str, episode: Episode):
        pass
