import logging
import os

from watchdog.observers import Observer

from episode_organizer.daemon.watch_handler import WatchHandler


class Watcher:
    """
    The watcher is the starting point for the tv show organizing service. It watches a single
    directory and notifies the TV Show Organizer once a new file or directory is detected on that
    directory.
    """

    logger = logging.getLogger('watcher')

    def __init__(self, watch_dir):
        """ Initializes the watch service, but does not start it! """
        self._watch_dir = watch_dir
        self._observer = Observer()
        self._handlers = []

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
        self._observer.schedule(handler.base_handler, self._watch_dir, recursive=False)
        self._handlers.append(handler)

    @property
    def watch_dir(self):
        return self._watch_dir

    def change_watch_dir(self, new_watch_dir: str):
        """
        Changes the directory being watched. Changes to the previous directory will no longer be
        detected.
         
        :param new_watch_dir: the new directory to be watched.
        :raises FileNotFoundError: if the given directory does not exist.
        """
        if not os.path.isdir(new_watch_dir):
            raise FileNotFoundError("New watch directory does not exist: %s" % new_watch_dir)

        # Unschedule all watches
        self._observer.unschedule_all()

        self._watch_dir = new_watch_dir

        for handler in self._handlers:
            self._observer.schedule(handler.base_handler, self._watch_dir, recursive=False)
