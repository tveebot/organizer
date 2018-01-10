import logging
import threading
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

        # Event to indicate the main loop exited
        # Initially the event must be set
        self._exited = threading.Event()
        self._exited.set()

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
        self._exited.clear()
        try:
            self._observer.start()
            self._last_watch = self._observer.schedule(Watcher.Handler(self), str(self.watch_dir))
            self._observer.join()
            self._observer.unschedule_all()
            self._last_watch = None
        finally:
            self._exited.set()

    def shutdown(self):
        """ Tells the loop in *run_forever()* to stop """
        self._observer.stop()

    def wait(self, timeout: float = None) -> bool:
        """
        Blocks while the watcher is running. If the watcher is not running it returns immediately.
        Otherwise, blocks until the watcher shuts down or until the *timeout* occurs.

        When the timeout argument is present and not None, it should be a floating point number
        specifying a timeout in seconds (or fractions thereof).

        This method returns true if and only if the internal flag has been set to true,
        either before the wait call or after the wait starts, so it will always return True
        except if a timeout is given and the operation times out.
        """
        return self._exited.wait(timeout)
