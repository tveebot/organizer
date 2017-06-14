import logging
from threading import Thread
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from episode_organizer.daemon.organizer import Organizer
from episode_organizer.xmlrpc_errors import raise_faults


class Configurator(Thread):
    """
    The configurator service provides a mechanism to change the configuration options dynamically.
    It is implemented as a simple XML-RPC server and provides methods to read and modify each configuration parameter.
    """

    logger = logging.getLogger('configurator')

    def __init__(self, config, config_file, organizer: Organizer, bind_address=("localhost", 8000)):
        """ Associates the configurator with an organizer and sets the bind address for the service """
        super().__init__()
        self._config = config
        self.config_file = config_file
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
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def set_watch_dir(self, watch_dir):
        """
        Sets a new watch directory. The configuration file is also updated if and only if the change is valid.

        :param watch_dir: the directory to set as watch directory.
        :raise FileNotFoundError: If the given directory does not exist.
        """
        try:
            # Update the organizer before updating the config file
            # This way the config file is not updated if the new directory is not valid
            self._organizer.set_watch_dir(watch_dir)

            # Update the config file
            self._config['DEFAULT']['WatchDirectory'] = watch_dir
            with open(self.config_file, "w") as file:
                self._config.write(file)
                Configurator.logger.debug("WatchDirectory parameter was updated in the config file")

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
        Sets a new storage directory. The configuration file is also updated if and only if the change is valid.

        :param storage_dir: the directory to set as storage directory.
        :raise FileNotFoundError: If the given directory does not exist.
        """
        try:
            # Update the organizer before updating the config file
            # This way the config file is not updated if the new directory is not valid
            self._organizer.storage_dir = storage_dir

            # Update the config file
            self._config['DEFAULT']['StorageDirectory'] = storage_dir
            with open(self.config_file, "w") as file:
                self._config.write(file)
                Configurator.logger.debug("StorageDirectory parameter was updated in the config file")

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

    @raise_faults()
    def set_watch_dir(self, watch_dir):
        self.configurator.set_watch_dir(watch_dir)

    @raise_faults()
    def watch_dir(self):
        return self.configurator.watch_dir()

    @raise_faults()
    def set_storage_dir(self, storage_dir):
        self.configurator.set_storage_dir(storage_dir)

    @raise_faults()
    def storage_dir(self):
        return self.configurator.storage_dir()
