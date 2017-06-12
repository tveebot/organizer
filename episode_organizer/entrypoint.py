"""
Episode Organizer

Usage:
  episode_organizer [ --conf=<config_file> ] [ --logs=<logs_config> ]
  episode_organizer (-h | --help)

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import logging
import os
import sys
from configparser import ConfigParser
from logging.config import fileConfig

from docopt import docopt
from pkg_resources import resource_filename, Requirement

from episode_organizer.configurator import Configurator
from episode_organizer.filter import Filter
from episode_organizer.mapper import Mapper
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


class EntryPoint:

    DEFAULT_CONFIG_FILE_LOCATION = os.path.join(os.getenv("HOME"), ".config", "episode_organizer")
    DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_FILE_LOCATION, "config.ini")

    config_file = DEFAULT_CONFIG_FILE
    config = ConfigParser()
    logger = logging.getLogger()
    organizer = None
    configurator = None

    def main(self):
        args = docopt(__doc__, version='TV Show Organizer Version 0.1')

        self.load_configurations(config_file=args['--conf'])
        self.setup_loggers(logs_config_file=args['--logs'])
        self.setup_organizer()
        self.setup_configurator()

        try:
            self.start_services()
            self.serve_forever()

        except KeyboardInterrupt:
            self.stop_services()

        except Exception:
            self.logger.exception("Caught an unexpected exception")
            self.stop_services()

    def load_configurations(self, config_file):

        # Always load the default configuration file
        # The configurations in this file are overridden by the ones defined in the configuration file provided
        # by the user, if the user provides one.
        default_config = resource_filename(Requirement.parse("episode_organizer"), 'episode_organizer/default.ini')

        self.config.read(default_config)

        if config_file:

            # User provided a path for a configuration file
            # Changes to the configurations will be updated to this file
            self.config_file = config_file

            if os.path.isfile(config_file):
                # Override configurations in the default conf file
                self.config.read(config_file)
            else:
                self.logger.warning("Config file does not exist yet: using default configurations")

        else:
            # Use the config file in the default location
            # Changes to the configurations will be updated to this file
            os.makedirs(self.DEFAULT_CONFIG_FILE_LOCATION, exist_ok=True)
            self.config_file = self.DEFAULT_CONFIG_FILE

    def setup_loggers(self, logs_config_file):

        if logs_config_file:

            # User provided a config file for the loggers
            # Will use this configuration
            if not os.path.isfile(logs_config_file):
                self.logger.error("The loggers file indicated does not exist: %s" % logs_config_file)
                sys.exit(1)

            fileConfig(logs_config_file)

        else:
            # Use the default
            fileConfig(self.DEFAULT_CONFIG_FILE)

        self.logger = logging.getLogger()

    def setup_organizer(self):

        # Check if both the watch and storage directories exist
        watch_dir = self.config['DEFAULT']['WatchDirectory']
        storage_dir = self.config['DEFAULT']['StorageDirectory']

        if not os.path.isdir(watch_dir):
            self.logger.error("Watch directory does not exist: %s" % watch_dir)
            sys.exit(1)

        if not os.path.isdir(storage_dir):
            self.logger.error("Storage directory does not exist: %s" % storage_dir)
            sys.exit(1)

        # Setup each component
        episode_filter = Filter()
        mapper = Mapper()
        storage_manager = StorageManager(storage_dir)

        self.organizer = Organizer(watch_dir, episode_filter, mapper, storage_manager)

    def setup_configurator(self):

        address = self.config['DEFAULT']['ConfiguratorAddress']
        port = self.config.getint('DEFAULT', 'ConfiguratorPort')

        self.configurator = Configurator(self.config, self.config_file, self.organizer, bind_address=(address, port))

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
    EntryPoint().main()
