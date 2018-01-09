from watchdog.events import FileSystemEventHandler, FileSystemEvent


class WatchHandler:
    """
    WatchHandler defines an interface with two methods: on_new_file and on_new_directory. These
    methods are called by the watcher once a new file or a new directory is detected on the watch
    directory. Classes that implement this interface should implement this methods to determine
    the actions to be taken once a new file/directory is detected.
    """

    def __init__(self):
        self.base_handler = _BaseHandler(self)

    def on_new_file(self, file_path):
        """ Called once a new file is detected on the watch directory """
        pass

    def on_new_directory(self, dir_path):
        """ Called once a new directory is detected on the watch directory """
        pass


class _BaseHandler(FileSystemEventHandler):
    """
    This is just a wrapper around a FileSystemEventHandler to call the correct watch handler
    methods once a new file or directory are detected.
    """

    def __init__(self, watch_handler):
        self.watch_handler = watch_handler

    def on_created(self, event: FileSystemEvent):

        if event.is_directory:
            self.watch_handler.on_new_directory(event.src_path)
        else:
            self.watch_handler.on_new_file(event.src_path)
