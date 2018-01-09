"""
Episode Organizer

Usage:
  episode-organizer-daemon [ --conf=<config_file> ] [ --logs=<logs_config> ]
  episode-organizer-daemon (-h | --help)

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import configparser
import logging
import os
import re
import signal
import sys
from logging.config import fileConfig

from docopt import docopt

from episode_organizer.daemon.configuration import Configuration
from episode_organizer.daemon.configurator import Configurator
from episode_organizer.daemon.filter import Filter
from episode_organizer.daemon.mapper import Mapper
from episode_organizer.daemon.organizer import Organizer
from episode_organizer.daemon.storage_manager import StorageManager


class Daemon:
    DEFAULT_USER_CONFIG_DIRECTORY = os.path.join(os.getenv("HOME"), ".config", "episode_organizer")
    DEFAULT_USER_CONFIG_FILE = os.path.join(DEFAULT_USER_CONFIG_DIRECTORY, "config.ini")

    ip_pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|"
                            "[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

    hostname_pattern = re.compile("^(([a-zA-Z0-9]|"
                                  "[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|"
                                  "[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

    logger = logging.getLogger()
    config = Configuration()
    config_file = None
    loggers_config_file = None
    organizer = None
    configurator = None

    def main(self):

        def stop_services(signum, frame):
            self.stop_services()

        # A terminate signal stops all services
        signal.signal(signal.SIGTERM, stop_services)

        args = docopt(__doc__, version='TV Show Organizer: Daemon Version 0.2')

        try:
            self.load_configurations(user_config_file=args['--conf'])
            self.setup_loggers(logs_config_file=args['--logs'])
            self.logger = logging.getLogger()
            self.setup_organizer()
            self.setup_configurator()

        except (configparser.Error, ValueError, FileNotFoundError) as error:
            self.logger.error(str(error))
            sys.exit(1)

        except Exception:
            self.logger.exception("Caught an unexpected exception while setting up")
            sys.exit(1)

        # Once everything is setup, start running the service

        try:
            self.start_services()
            self.serve_forever()

        except KeyboardInterrupt:
            self.stop_services()
            # exit correctly

        except OSError as error:
            self.logger.error(str(error))
            self.stop_services()

        except Exception:
            self.logger.exception("Caught an unexpected exception while running")
            self.stop_services()
            sys.exit(1)

    def load_configurations(self, user_config_file):

        if user_config_file:

            # User provided a path for a configuration file
            # Changes to the configurations will be updated to this file
            self.config_file = user_config_file

        else:
            # Use the config file in the default location
            # Changes to the configurations will be updated to this file
            os.makedirs(self.DEFAULT_USER_CONFIG_DIRECTORY, exist_ok=True)
            self.config_file = self.DEFAULT_USER_CONFIG_FILE

        try:
            self.config.load(self.config_file)
        except FileNotFoundError:
            self.logger.warning("Config file does not exist yet: using default configurations")

    def setup_loggers(self, logs_config_file):

        if logs_config_file:

            # User provided a config file for the loggers
            # Will use this configuration
            if not os.path.isfile(logs_config_file):
                raise FileNotFoundError("The loggers file indicated does not exist: %s" %
                                        logs_config_file)

            self.loggers_config_file = logs_config_file

        else:
            # Use the default
            self.loggers_config_file = Configuration.default_config_file

        fileConfig(self.loggers_config_file)

    def setup_organizer(self):

        # Check if both the watch and storage directories exist
        watch_dir = self.config['WatchDirectory']
        storage_dir = self.config['StorageDirectory']

        if not os.path.isdir(watch_dir):
            raise FileNotFoundError("Watch directory does not exist: %s" % watch_dir)

        if not os.path.isdir(storage_dir):
            raise FileNotFoundError("Storage directory does not exist: %s" % storage_dir)

        # Setup each component
        episode_filter = Filter()
        mapper = Mapper()
        storage_manager = StorageManager(storage_dir)

        self.organizer = Organizer(watch_dir, episode_filter, mapper, storage_manager)

    def setup_configurator(self):

        address = self.config['ConfiguratorAddress']

        if not self.ip_pattern.match(address) and not self.hostname_pattern.match(address):
            raise ValueError("The address '%s' is not a valid ip or hostname" % address)

        try:
            port = int(self.config['ConfiguratorPort'])

            if not (0 < port < 65536):
                raise ValueError

        except ValueError:
            raise ValueError("The port '%s' is not valid" % self.config['ConfiguratorPort'])

        self.configurator = Configurator(self.config_file, self.config, self.organizer,
                                         bind_address=(address, port))

    def start_services(self):
        self.logger.info("Starting organizer service...")
        self.organizer.start()
        self.logger.info("Starting configurator service...")
        self.configurator.start()

    def serve_forever(self):
        self.logger.info("Running...")
        self.organizer.join()
        self.configurator.join()

    def stop_services(self):
        self.logger.info("Stopping the organizer service...")
        self.organizer.stop()
        self.logger.info("Stopping the configurator service...")
        self.configurator.stop()

        self.logger.info("All services were stopped")


if __name__ == '__main__':
    Daemon().main()
