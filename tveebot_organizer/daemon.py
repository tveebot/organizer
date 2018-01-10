"""
TVeeBot Organizer

Usage:
  tveebot-organizerd [options]

Options:
  -h --help                  Show this screen.
  -V --version               Show version.
  -w --watch=<directory>     Set watch directory.
  -l --library=<directory>   Set library directory.
  -o --log=<file>            Set file to output logs to.
  -c --conf=<file>           Specify a configuration file.
"""
import configparser
import logging
import sys
from logging.config import fileConfig
from pathlib import Path

from docopt import docopt
from pkg_resources import resource_filename

from tveebot_organizer.filter import Filter
from tveebot_organizer.matcher import Matcher
from tveebot_organizer.organizer import Organizer
from tveebot_organizer.storage_manager import StorageManager
from tveebot_organizer.watcher import Watcher

DEFAULT_CONFIG_FILE = resource_filename(__name__, 'config.ini')

logger = logging.getLogger()
config = configparser.ConfigParser()


def main():
    args = docopt(__doc__, version="TVeeBot Organizer: 1.0")

    # Load the default configurations first
    config.read(DEFAULT_CONFIG_FILE)

    # Setup all loggers
    fileConfig(config)

    if args['--log']:
        log_path = Path(args['--log'])

        try:
            handler = logging.FileHandler(str(log_path))
        except OSError as error:
            logger.error("failed to setup log file: %s" % str(error))
            sys.exit(1)

        # Get handler from default logger
        # This is sort of an hack to get the formatter define in the default configuration file
        default_handler = logger.handlers[0]
        handler.setFormatter(default_handler.formatter)

        # Add handler to each logger
        loggers = [
            logging.getLogger(),
            logging.getLogger('organizer'),
            logging.getLogger('storageManager'),
            logging.getLogger('watcher'),
        ]

        # noinspection PyShadowingNames
        for log in loggers:
            log.addHandler(handler)

    if args['--conf']:
        config_file = Path(args['--conf'])

        try:
            with open(str(config_file)) as file:
                config.read_file(file)
        except FileNotFoundError:
            logger.error("config file was not found: %s" % config_file)

    if args['--watch']:
        config['watcher']['watch'] = args['--watch']

    if args['--library']:
        config['organizer']['library'] = args['--library']

    try:
        watch_dir = Path(config['watcher']['watch'])
    except KeyError:
        logger.error("watch directory is not specified")
        logger.info("use option '--watch' to specify watch directory")
        sys.exit(1)

    try:
        library_dir = Path(config['organizer']['library'])
    except KeyError:
        logger.error("library directory is not specified")
        logger.info("use option '--library' to specify library directory")
        sys.exit(1)

    if not watch_dir.is_dir():
        logger.error("watch directory not found: %s" % watch_dir)
        sys.exit(1)

    if not library_dir.is_dir():
        logger.error("library directory not found: %s" % library_dir)
        sys.exit(1)

    organizer = Organizer(
        filter=Filter(),
        matcher=Matcher(),
        storage_manager=StorageManager(library_dir)
    )

    watcher = Watcher(watch_dir, organizer)

    try:
        logger.info("running...")
        watcher.run_forever()
    except KeyboardInterrupt:
        logger.info("exiting...")
    except:
        logger.exception("unexpected error")

    watcher.shutdown()
    if watcher.wait(timeout=10):
        logger.info("exited cleanly")
    else:
        logger.info("exited abruptly")


if __name__ == '__main__':
    main()
