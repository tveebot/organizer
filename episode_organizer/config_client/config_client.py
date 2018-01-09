from xmlrpc.client import ServerProxy

from episode_organizer.xmlrpc_errors import expect_faults


class ConfigClient:

    def __init__(self, server_address):
        self._configurator = ServerProxy('http://%s:%s' % (server_address[0], server_address[1]),
                                         allow_none=True)

    @expect_faults()
    def set_config(self, key, value):
        self._configurator.set_config(key, value)

    @expect_faults()
    def get_config(self, key):
        return self._configurator.get_config(key)
