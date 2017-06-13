from xmlrpc.client import ServerProxy


class ConfigClient:

    def __init__(self, server_address):

        self._config_methods = {
            'WatchDirectory': self.set_watch_dir,
            'StorageDirectory': self.set_storage_dir,
        }

        self._configurator = ServerProxy('http://%s:%s' % (server_address[0], server_address[1]), allow_none=True)

    def set_config(self, key, value):
        set_method = self._config_methods[key]
        set_method(value)

    def set_watch_dir(self, value):
        self._configurator.set_watch_dir(value)

    def set_storage_dir(self, value):
        self._configurator.set_storage_dir(value)
