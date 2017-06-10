"""
TV Show Organizer

Usage:
  tvshow_organizer --conf=<config_file>
  tvshow_organizer (-h | --help)

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

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.organizer import Organizer
from show_organizer.storage_manager import StorageManager


def main():
    args = docopt(__doc__, version='TV Show Organizer Version 0.1')

    config_file = args['--conf']

    if not os.path.isfile(config_file):
        print("Error: config file '%s' does not exist" % config_file, file=sys.stderr)
        sys.exit(1)

    # setup loggers
    fileConfig(config_file)
    logger = logging.getLogger()

    # load configuration file
    config = ConfigParser()
    config.read(config_file)

    watch_dir = config['DEFAULT']['WatchDirectory']
    storage_dir = config['DEFAULT']['StorageDirectory']

    if not os.path.isdir(watch_dir):
        logger.error("Watch directory does not exist: %s" % watch_dir)
        sys.exit(1)

    if not os.path.isdir(storage_dir):
        logger.error("Storage directory does not exist: %s" % storage_dir)
        sys.exit(1)

    # start service
    episode_filter = Filter()
    mapper = Mapper()
    storage_manager = StorageManager(storage_dir)

    organizer = Organizer(watch_dir, episode_filter, mapper, storage_manager)

    try:
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
