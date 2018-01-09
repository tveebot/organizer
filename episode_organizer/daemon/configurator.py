import logging
from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from episode_organizer.daemon.configuration import Configuration
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.xmlrpc_errors import raise_faults

logger = logging.getLogger('configurator')


class Configurator(Thread):
    """
    The configurator service provides a mechanism to change the configuration options
    dynamically. It is implemented as a simple XML-RPC server and provides methods to read and
    modify each configuration parameter.
    """

    def __init__(self, config_file, config: Configuration, organizer: Organizer,
                 bind_address=("localhost", 35121)):
        """
        Associates the configurator with an organizer and sets the bind address for the service.
        """
        super().__init__()
        self.config_file = config_file
        self._config = config
        self._organizer = organizer
        self._bind_address = bind_address
        self._server = None

        self.set_methods = {
            'WatchDirectory': self.set_watch_dir,
            'StorageDirectory': self.set_storage_dir,
        }

    def start(self):
        """
        Starts the configurator service.
        Binds to the given address and starts listening for requests.
        """
        self._server = SimpleXMLRPCServer(self._bind_address, SimpleXMLRPCRequestHandler,
                                          allow_none=True)
        self._server.register_instance(_ConfiguratorInterface(self))
        super().start()

    def run(self):
        """ Runs the service """
        self._server.serve_forever()

    def stop(self):
        """
        Stops the service.
        This method should always be called before exiting the application.
        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def set_config(self, key, value):
        """
        Sets a new value for a configuration key. Provided the given configuration key is valid
        and the given value is valid for that key, the entire system is updated to use the new
        value. This method is exception safe, which means that if any exception is raised,
        then the configuration and the system are kept in the previous state.
        """
        try:
            # If the key is not contained in the 'set_methods' dict, then it is not valid or is
            # not editable Do not use the configuration getitem method to test if a key is valid
            # because it will not raise a key error for non-editable keys
            set_method = self.set_methods[key]

        except KeyError:
            message = "Key '%s' is invalid" % key
            logger.warning(message)
            raise KeyError(message)

        previous_value = self._config[key]
        self._config.update(self.config_file, key, value)

        try:
            set_method(value)

        except:
            # Rollback configuration value
            self._config.update(self.config_file, key, previous_value)
            raise

    def get_config(self, key):
        """ 
        Returns the current value for the given key if the kye is valid.  
        
        :return: the current value for the given configuration key
        :raises KeyError: if the given key is invalid.
        """
        return self._config[key]

    def set_watch_dir(self, watch_dir):

        try:
            self._organizer.set_watch_dir(watch_dir)

        except (FileNotFoundError, OSError):
            logger.error("Failed to set new watch directory: directory '%s' does not exist",
                              watch_dir)
            raise

    def set_storage_dir(self, storage_dir):

        try:
            self._organizer.set_storage_dir(storage_dir)

        except (FileNotFoundError, OSError):
            logger.error("Failed to set new storage directory: directory '%s' does not exist",
                              storage_dir)
            raise


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
