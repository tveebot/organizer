import os
import sys
import logging
from logging.config import fileConfig

from show_organizer.filter import Filter
from show_organizer.mapper import Mapper
from show_organizer.organizer import Organizer
from show_organizer.storage_manager import StorageManager


def main():

    # setup loggers
    logging_conf_file = '../default.ini'

    if not os.path.isfile(logging_conf_file):
        print("Config file '%s' does not exist" % logging_conf_file, file=sys.stderr)
        sys.exit(1)

    fileConfig(logging_conf_file)
    logger = logging.getLogger()

    # load configuration file
    watch_dir = "../watch"
    storage_dir = "../storage"

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
