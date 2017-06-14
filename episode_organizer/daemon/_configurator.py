import logging
import os
from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from episode_organizer.daemon.configuration import Configuration
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.xmlrpc_errors import raise_faults


class Configurator(Thread):
    """
    The configurator service provides a mechanism to change the configuration options dynamically.
    It is implemented as a simple XML-RPC server and provides methods to read and modify each configuration parameter.
    """

    logger = logging.getLogger('configurator')

    def __init__(self, config: Configuration, organizer: Organizer, bind_address=("localhost", 35121)):
        """ Associates the configurator with an organizer and sets the bind address for the service """
        super().__init__()
        self._config = config
        self._organizer = organizer
        self._bind_address = bind_address
        self._server = None

        self.set_methods = {
            'WatchDirectory': self.set_watch_dir,
            'StorageDirectory': self.set_storage_dir,
        }

    def start(self):
        self._server = SimpleXMLRPCServer(self._bind_address, SimpleXMLRPCRequestHandler, allow_none=True)
        self._server.register_instance(_ConfiguratorInterface(self))
        super().start()

    def run(self):
        """ Runs the service waiting for new requests """
        self._server.serve_forever()

    def stop(self):
        """ Stops the service. This method should be called before exiting the application """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def set_config(self, key, value):

        try:
            set_method = self.set_methods[key]
            set_method(value)

        except KeyError:
            message = "Key '%s' is invalid" % key
            self.logger.warning(message)
            raise KeyError(message)

        self._config[key] = value

    def get_config(self, key):
        return self._config[key]

    def set_watch_dir(self, watch_dir):

        if not os.path.isdir(watch_dir):
            message = "Failed to change watch directory: directory '%s' does not exist" % watch_dir
            self.logger.warning(message)
            raise FileNotFoundError(message)

        self._organizer.set_watch_dir(watch_dir)

    def set_storage_dir(self, storage_dir):

        if not os.path.isdir(storage_dir):
            message = "Failed to change storage directory: directory '%s' does not exist" % storage_dir
            self.logger.warning(message)
            raise FileNotFoundError(message)

        self._organizer.set_storage_dir(storage_dir)


class _ConfiguratorInterface:
    """ This class defines the actual interface provided to the clients """

    def __init__(self, configurator):
        self.configurator = configurator

    @raise_faults()
    def set_config(self, key, value):
        self.configurator.set_config(key, value)

    @raise_faults()
    def get_config(self, key):
        return self.configurator.get_config(key)
