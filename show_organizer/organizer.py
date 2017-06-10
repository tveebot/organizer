import os

import shutil

from show_organizer.episode import Episode


class Organizer:

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir

    def get_episode_directory(self, episode: Episode):
        return os.path.join(self.storage_dir, episode.tvshow.name, "Season %02d" % episode.season)

    def store(self, video_file: str, episode: Episode):

        move_dir = self.get_episode_directory(episode)

        # Make sure the directory exists
        os.makedirs(move_dir, exist_ok=True)

        try:
            # Only then, move the file to the directory
            shutil.move(video_file, move_dir)

        except shutil.Error:
            raise FileExistsError("File '%s' already exists in '%s'" %
                                  (os.path.basename(video_file), os.path.relpath(move_dir, start=self.storage_dir)))
