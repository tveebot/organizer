from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

import logging

from episode_organizer.organizer import Organizer


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class Configurator(Thread):

    def __init__(self, organizer: Organizer):
        super().__init__()
        self._server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
        self._server.register_instance(_Configurator(organizer))

    def run(self):
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()


class _Configurator:

    logger = logging.getLogger('configurator')

    def __init__(self, organizer: Organizer):
        self.organizer = organizer

    def set_watch_dir(self, watch_dir):

        try:
            self.organizer.set_watch_dir(watch_dir)

        except FileNotFoundError as error:
            self.logger.warning(str(error))
            raise error

    def watch_dir(self):
        return self.organizer.watch_dir
