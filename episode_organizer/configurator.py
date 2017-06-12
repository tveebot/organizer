from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

import logging

from episode_organizer.organizer import Organizer


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class Configurator(Thread):

    logger = logging.getLogger('configurator')

    def __init__(self, organizer: Organizer, bind_address=("localhost", 8000)):
        super().__init__()
        self._server = SimpleXMLRPCServer(bind_address, requestHandler=RequestHandler, allow_none=True)
        self._server.register_instance(_Configurator(organizer))

    def run(self):
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()


class _Configurator:

    def __init__(self, organizer: Organizer):
        self.organizer = organizer

    def set_watch_dir(self, watch_dir):

        try:
            self.organizer.set_watch_dir(watch_dir)
            Configurator.logger.info("Watch directory was changed to: %s" % watch_dir)

        except FileNotFoundError as error:
            Configurator.logger.warning("Tried changing watch directory to '%s', but that directory did not exist. "
                                        "Kept previous watch directory" % watch_dir)
            raise error

    def watch_dir(self):
        return self.organizer.watch_dir

    def set_storage_dir(self, storage_dir):

        try:
            self.organizer.storage_dir = storage_dir
            Configurator.logger.info("Storage directory was changed to: %s" % storage_dir)

        except FileNotFoundError as error:
            Configurator.logger.warning("Tried changing storage directory to '%s', but that directory did not exist. "
                                        "Kept previous storage directory" % storage_dir)
            raise error

    def storage_dir(self):
        return self.organizer.storage_dir
