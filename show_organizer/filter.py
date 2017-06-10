import os


class Filter:

    video_extensions = {'.mkv', '.mp4', '.avi', '.m4p', '.m4v'}

    def get_episode_file(self, path):

        if os.path.isdir(path):

            # Look inside the directory for the biggest video file
            episode_file = None
            max_size = -1

            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                file_size = os.path.getsize(file_path)

                if self.is_video_file(file_path) and file_size > max_size:
                    episode_file = file_path
                    max_size = file_size

            if episode_file is None:
                raise ValueError("The directory '%s' does not contain any video file" % path)

            return episode_file

        elif os.path.isfile(path) and self.is_video_file(path):
            return path

        else:
            raise ValueError("The path '%s' is not a video file" % path)

    @staticmethod
    def is_video_file(file_path):

        if not os.path.isfile(file_path):
            return False

        path, extension = os.path.splitext(file_path)

        return extension.lower() in Filter.video_extensions
