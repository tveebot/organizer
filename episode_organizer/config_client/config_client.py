class ConfigClient:

    def __init__(self, server_address):

        self._config_methods = {
            'WatchDirectory': self.set_watch_dir,
            'StorageDirectory': self.set_storage_dir,
        }

    def set_config(self, key, value):
        set_method = self._config_methods[key]
        set_method(value)

    def set_watch_dir(self, value):
        pass

    def set_storage_dir(self, value):
        pass
