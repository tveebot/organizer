"""
Episode Organizer

Usage:
  episode-organizer-cli -g <key> [ --host=HOST ] [ --port=PORT ] [ -v | --verbose ]
  episode-organizer-cli -s <key> <value> [ --host=HOST ] [ --port=PORT ] [ -v | --verbose ]
  episode-organizer-cli (-h | --help)

Options:
  -h --help       Show this screen.
  -v --verbose    Show this screen.
  --host=HOST     Hostname or ip address of the daemon [default: localhost].
  --port=PORT     Port where the daemon is listening on [default: 35121].
  --version       Show version.

"""
import re

import logging

import sys
from docopt import docopt

from episode_organizer.config_client.config_client import ConfigClient


class ClientCLI:

    ip_pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|"
                            "2[0-4][0-9]|25[0-5])$")

    hostname_pattern = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|"
                                  "[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

    client = None
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    def main(self):
        args = docopt(__doc__, version='Episode Organizer: Client - Version 0.1')
        self.run(args)

    def run(self, args):

        self.client = self.setup_client(args['--host'], args['--port'])

        if args['--verbose']:
            self.logger.setLevel(logging.DEBUG)

        try:
            if args['-g']:
                self.get_config(args['<key>'])

            else:  # option is -s
                self.set_config(args['<key>'], args['<value>'])

        except FileNotFoundError as error:
            self.logger.error(str(error))
            sys.exit(1)

        except KeyError:
            self.logger.error("The key '%s' is not a valid configuration key" % args['<key>'])
            sys.exit(1)

    def setup_client(self, host, port):

        if not self.ip_pattern.match(host) and not self.hostname_pattern.match(host):
            raise ValueError("Hostname '%s' is not valid" % host)

        try:
            port = int(port)
        except ValueError:
            raise ValueError("Port '%s' is not valid" % port)

        if not (0 < port < 65536):
            raise ValueError("Port '%d' is not valid" % port)

        return ConfigClient(server_address=(host, port))

    def get_config(self, key):

        self.logger.debug("Obtaining value for key '%s'" % key)
        value = self.client.get_config(key)
        self.logger.info("%s: %s" % (key, value))

    def set_config(self, key, value):

        self.logger.debug("Setting value '%s' for key '%s'" % (key, value))
        self.client.set_config(key, value)
        self.logger.info("Key '%s' was set to '%s'" % (key, value))


if __name__ == '__main__':
    ClientCLI().main()
