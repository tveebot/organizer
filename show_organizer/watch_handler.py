from watchdog.events import FileSystemEventHandler, FileSystemEvent


class WatchHandler:

    def __init__(self):
        self.base_handler = _BaseHandler(self)

    def on_new_file(self, file_path):
        pass

    def on_new_directory(self, dir_path):
        pass


class _BaseHandler(FileSystemEventHandler):

    def __init__(self, watch_handler):
        self.watch_handler = watch_handler

    def on_created(self, event: FileSystemEvent):

        if event.is_directory:
            self.watch_handler.on_new_directory(event.src_path)
        else:
            self.watch_handler.on_new_file(event.src_path)
