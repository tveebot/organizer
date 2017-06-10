from show_organizer.watch_handler import WatchHandler
from watchdog.observers import Observer


class Watcher:
    """
    The watcher is the starting point for the tv show organizing service. It watches a single directory and notifies
    the TV Show Organizer once a new file or directory is detected on that directory.
    """

    def __init__(self, watch_dir):
        """ Initializes the watch service, but does not start it! """
        self.watch_dir = watch_dir
        self._observer = Observer()

    def start(self):
        """ Starts the watch service on the background """
        self._observer.start()

    def stop(self):
        """ Signals the watch service to terminate """
        self._observer.stop()

    def join(self):
        """ Waits for the watch service to terminate """
        self._observer.join()

    def add_handler(self, handler: WatchHandler):
        """ Adds a new watch handler to the service """
        self._observer.schedule(handler.base_handler, self.watch_dir, recursive=False)
