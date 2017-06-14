from xmlrpc.client import ServerProxy

from episode_organizer.xmlrpc_errors import expect_faults


class ConfigClient:

    def __init__(self, server_address):

        self._config_set_methods = {
            'WatchDirectory': self.set_watch_dir,
            'StorageDirectory': self.set_storage_dir,
        }

        self._config_get_methods = {
            'WatchDirectory': self.watch_dir,
            'StorageDirectory': self.storage_dir,
        }

        self._configurator = ServerProxy('http://%s:%s' % (server_address[0], server_address[1]), allow_none=True)

    def set_config(self, key, value):
        set_method = self._config_set_methods[key]
        set_method(value)

    def get_config(self, key):
        get_method = self._config_get_methods[key]
        return get_method()

    @expect_faults()
    def watch_dir(self):
        return self._configurator.watch_dir()

    @expect_faults()
    def set_watch_dir(self, value):
        self._configurator.set_watch_dir(value)

    @expect_faults()
    def storage_dir(self):
        return self._configurator.storage_dir()

    @expect_faults()
    def set_storage_dir(self, value):
        self._configurator.set_storage_dir(value)
