import logging

from show_organizer.watch_handler import WatchHandler
from watchdog.observers import Observer


class Watcher:
    """
    The watcher is the starting point for the tv show organizing service. It watches a single directory and notifies
    the TV Show Organizer once a new file or directory is detected on that directory.
    """

    logger = logging.getLogger('watcher')

    def __init__(self, watch_dir):
        """ Initializes the watch service, but does not start it! """
        self.watch_dir = watch_dir
        self._observer = Observer()

        self.logger.info("Watch directory: %s" % self.watch_dir)

    def start(self):
        """ Starts the watch service on the background """
        self._observer.start()
        self.logger.debug("Started watcher")

    def stop(self):
        """ Signals the watch service to terminate """
        self._observer.stop()
        self.logger.debug("Sent stop signal to watcher")

    def join(self):
        """ Waits for the watch service to terminate """
        self._observer.join()
        self.logger.debug("Watcher has terminated")

    def add_handler(self, handler: WatchHandler):
        """ Adds a new watch handler to the service """
        self._observer.schedule(handler.base_handler, self.watch_dir, recursive=False)
