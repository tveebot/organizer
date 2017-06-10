from show_organizer.watch_handler import WatchHandler
from watchdog.observers import Observer


class Watcher:

    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self._observer = Observer()

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()

    def add_handler(self, handler: WatchHandler):
        self._observer.schedule(handler.base_handler, self.watch_dir, recursive=False)
