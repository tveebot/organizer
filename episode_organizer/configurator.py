from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

import logging

from episode_organizer.organizer import Organizer


class Configurator(Thread):
    """
    The configurator service provides a mechanism to change the configuration options dynamically.
    It is implemented as a simple XML-RPC server and provides methods to read and modify each configuration parameter.
    """

    logger = logging.getLogger('configurator')

    def __init__(self, organizer: Organizer, bind_address=("localhost", 8000)):
        """ Associates the configurator with an organizer and sets the bind address for the service """
        super().__init__()
        self._organizer = organizer
        self._bind_address = bind_address
        self._server = None

    def start(self):
        self._server = SimpleXMLRPCServer(self._bind_address, SimpleXMLRPCRequestHandler, allow_none=True)
        self._server.register_instance(_ConfiguratorInterface(self))
        super().start()

    def run(self):
        """ Runs the service waiting for new requests """
        self._server.serve_forever()

    def stop(self):
        """ Stops the service. This method should be called before exiting the application """
        self._server.shutdown()
        self._server.server_close()
        self._server = None

    def set_watch_dir(self, watch_dir):
        """
        Sets a new watch directory.

        :param watch_dir: the directory to set as watch directory.
        :raise FileNotFoundError: If the given directory does not exist.
        """
        try:
            self._organizer.set_watch_dir(watch_dir)
            Configurator.logger.info("Watch directory was changed to: %s" % watch_dir)

        except FileNotFoundError as error:
            Configurator.logger.warning("Tried changing watch directory to '%s', but that directory did not exist. "
                                        "Kept previous watch directory" % watch_dir)
            raise error

    def watch_dir(self):
        """ Returns the current watch directory being use """
        return self._organizer.watch_dir

    def set_storage_dir(self, storage_dir):
        """
        Sets a new storage directory.

        :param storage_dir: the directory to set as storage directory.
        :raise FileNotFoundError: If the given directory does not exist.
        """
        try:
            self._organizer.storage_dir = storage_dir
            Configurator.logger.info("Storage directory was changed to: %s" % storage_dir)

        except FileNotFoundError as error:
            Configurator.logger.warning("Tried changing storage directory to '%s', but that directory did not exist. "
                                        "Kept previous storage directory" % storage_dir)
            raise error

    def storage_dir(self):
        """ Returns the current storage directory being use """
        return self._organizer.storage_dir


class _ConfiguratorInterface:
    """ This class defines the actual interface provided to the clients """

    def __init__(self, configurator):
        self.configurator = configurator

    def set_watch_dir(self, watch_dir):
        self.configurator.set_watch_dir(watch_dir)

    def watch_dir(self):
        return self.configurator.watch_dir()

    def set_storage_dir(self, storage_dir):
        self.configurator.set_storage_dir(storage_dir)

    def storage_dir(self):
        return self.configurator.storage_dir()
