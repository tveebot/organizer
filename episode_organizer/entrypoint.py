"""
Episode Organizer

Usage:
  episode_organizer [ --conf=<config_file> ] [ --logs=<logs_config> ]
  episode_organizer (-h | --help)

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
import sys
import logging
from configparser import ConfigParser
from logging.config import fileConfig
from docopt import docopt
from pkg_resources import resource_filename, Requirement

from episode_organizer.filter import Filter
from episode_organizer.mapper import Mapper
from episode_organizer.organizer import Organizer
from episode_organizer.storage_manager import StorageManager


def main():
    args = docopt(__doc__, version='TV Show Organizer Version 0.1')

    # Load configurations
    config = ConfigParser()

    # Always load the default configuration file
    # The configurations in this file are overridden by the ones defined in the configuration file provided
    # by the user, if the user provides one.
    default_config = resource_filename(Requirement.parse("episode_organizer"), 'episode_organizer/default.ini')
    config.read(default_config)

    if args['--conf']:
        # User provided a configuration file
        config_file = args['--conf']

        if not os.path.isfile(config_file):
            print("Error: config file '%s' does not exist" % config_file, file=sys.stderr)
            sys.exit(1)

        # Override configurations in the default conf file
        config.read(config_file)

    # Setup loggers

    if args['--logs']:
        # User provided a config file for the logger
        logs_config_file = args['--logs']

        if not os.path.isfile(logs_config_file):
            print("Error: logs config file '%s' does not exist" % logs_config_file, file=sys.stderr)
            sys.exit(1)

        fileConfig(logs_config_file)

    else:
        # Use the default
        fileConfig(default_config)

    logger = logging.getLogger()

    # Validate configurations: check if both the watch and storage directories exist

    watch_dir = config['DEFAULT']['WatchDirectory']
    storage_dir = config['DEFAULT']['StorageDirectory']

    if not os.path.isdir(watch_dir):
        logger.error("Watch directory does not exist: %s" % watch_dir)
        sys.exit(1)

    if not os.path.isdir(storage_dir):
        logger.error("Storage directory does not exist: %s" % storage_dir)
        sys.exit(1)

    # Configure the organizer
    episode_filter = Filter()
    mapper = Mapper()
    storage_manager = StorageManager(storage_dir)

    organizer = Organizer(watch_dir, episode_filter, mapper, storage_manager)

    try:
        # Start the service in a thread and wait until it terminates
        organizer.start()
        logger.info("Started organizing service")

        organizer.join()

    except KeyboardInterrupt:
        logger.info("Stopping the service...")
        organizer.stop()

    except Exception:
        logger.exception("Caught an unexpected exception")

        logger.info("Stopping the service...")
        organizer.stop()

    logger.info("Service was stopped")


if __name__ == '__main__':
    main()
