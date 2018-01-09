import logging
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from tveebot_organizer.organizer import Organizer

logger = logging.getLogger('watching')


class Watcher:
    """
    The Watcher component watches a directory for new files or directories. It is associated with
    an organizer instance. This organizer is called every time a new file or directory is created.
    """

    class Handler(FileSystemEventHandler):
        """ Invokes the organizer every time a new file or directory is created """

        def __init__(self, watcher: 'Watcher'):
            self.watcher = watcher

        def on_created(self, event: FileSystemEvent):
            self.watcher.organizer.organize(Path(event.src_path))

    def __init__(self, watch_dir: Path, organizer: Organizer):
        """ Initializes the watching, but does not start it! """
        self.organizer = organizer
        self._observer = Observer()
        self._watch_dir = watch_dir

        # Stores the watch for the current watch directory
        # This watch is used when changing the current watch directory
        self._last_watch: ObservedWatch = None

    @property
    def watch_dir(self) -> Path:
        return self._watch_dir

    @watch_dir.setter
    def watch_dir(self, directory: Path):
        if self._last_watch is not None:
            # Start watching the new directory
            watch = self._observer.schedule(Watcher.Handler(self), str(directory))

            # Stop watching the previous directory
            self._observer.unschedule(self._last_watch)

            # Store the watch of the new directory to stop watching it when the watch directory is
            # changed again
            self._last_watch = watch

            self._watch_dir = directory

    def run_forever(self):
        """ Runs the watching until the *shutdown()* is called """
        self._observer.start()
        self._last_watch = self._observer.schedule(Watcher.Handler(self), str(self.watch_dir))
        self._observer.join()
        # self._observer.unschedule_all()
        self._last_watch = None

    def shutdown(self):
        """ Tells the loop in *run_forever()* to stop """
        self._observer.stop()
