"""
Episode Organizer

Usage:
  episode-organizer-cli [ --host=HOST ] [ --port=PORT ] -g <key>
  episode-organizer-cli [ --host=HOST ] [ --port=PORT ] -s <key> <value>
  episode-organizer-cli (-h | --help)

Options:
  -h --help       Show this screen.
  --host=HOST     Hostname or ip address of the daemon [default: localhost].
  --port=PORT     Port where the daemon is listening on [default: 35121].
  --version       Show version.

"""
from docopt import docopt

from episode_organizer.config_client.config_client import ConfigClient


class EntryPoint:

    client = None

    def main(self):
        args = docopt(__doc__, version='Episode Organizer: Client - Version 0.1')
        self.run(args)

    def run(self, args):

        self.client = self.setup_client(args['--host'], args['--port'])

        if args['-g']:
            self.client.get_config(args['<key>'])

        else:  # option is -s
            self.client.set_config(args['<key>'], args['<value>'])

    def setup_client(self, host, port):
        return ConfigClient(server_address=(host, int(port)))

    def get_config(self, key):
        self.client.get_config(key)

    def set_config(self, key, value):
        self.client.set_config(key, value)

if __name__ == '__main__':
    EntryPoint().main()
