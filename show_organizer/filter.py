import os


class Filter:

    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def get_episode_file(self, path):
        pass

    @staticmethod
    def is_video_file(file_path):

        if not os.path.isfile(file_path):
            return False

        path, extension = os.path.splitext(file_path)

        return extension.lower() in Filter.video_extensions
