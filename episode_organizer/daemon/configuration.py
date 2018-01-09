from configparser import ConfigParser

from pkg_resources import resource_filename, Requirement


class Configuration:
    """
    The configuration class provides an interface to access and modify the current configurations
    of the system. This class is supposed to work as close to a dictionary as possible.
    """

    default_config_file = resource_filename(
        Requirement.parse("episode_organizer"), 'episode_organizer/daemon/default.ini')

    def __init__(self):
        """ Initializes the configurations with the default values from the 'default.ini' file. """
        self._config = ConfigParser()
        self._config.read(self.default_config_file)

    @staticmethod
    def from_dict(config: dict):
        """
        Builds a configuration instance from a dictionary with the configurations. The keys mut
        be valid, otherwise a KeyError will be raised. If the dictionary does not define some
        configuration parameter, then the default value is used.

        :param config: the dictionary defining the configurations.
        :return: a new configuration instance initialized with the configurations provided in
                 the dictionary.
        """
        configuration = Configuration()
        for key, value in config.items():

            if key not in configuration._config['DEFAULT']:
                raise KeyError("Key '%s' is not a valid" % key)

            configuration._config['DEFAULT'][key] = value

        return configuration

    def load(self, config_file):
        """
        Loads the configuration file into memory. If the file does not exist, then it is ignored
        and the default values are kept.
        
        :param config_file:       the configuration file to load configurations from.
        :raise FileNotFoundError: if the config file does not exist.
        :raise PermissionError:   if the given key is invalid.
        :raise OSError:           if it fails to read the config file.
        """
        with open(config_file) as file:
            self.load_file(file)

    def load_file(self, file):
        """ The same as load but takes a file like object """
        self._config.read_file(file)

    def save(self, config_file):
        """
        Saves the current configuration in memory to the config file 

        :param config_file:       the path to the file to save configurations to.
        :raise KeyError:          if the provided key is not valid.
        :raise PermissionError:   if it fails to write to the config file.
        :raise FileNotFoundError: if it failed to create the config file because its directory
                                  does not exist.
        """
        # Update the configuration file
        with open(config_file, "w") as file:
            self.save_file(file)

    def save_file(self, file):
        """ The same as save but takes a file like object """
        self._config.write(file)

    def __getitem__(self, key):
        """
        Returns the current value for a configuration key.

        :param key:         the configuration key to obtain the value of.
        :return:            the value for the given key.
        :raises KeyError:   if the the given key is not valid.
        """
        return self._config['DEFAULT'][key]

    def __setitem__(self, key, value):
        """
        Sets a new value for a valid configuration key. Updates the configuration file.

        :param key:      configuration key to set value for.
        :param value:    value to set.
        :raise KeyError: if the provided key is not valid.
        """
        if key not in self._config['DEFAULT']:
            raise KeyError("Key '%s' is not a valid" % key)

        self._config['DEFAULT'][key] = value

    def update(self, config_file, key, value):
        """
        Calling this method is similar to calling __setitem__() followed by save(). An important
        difference is that if any error occurs while trying to save changes to the config file,
        then the configuration in memory is not changed as well.

        :param key:               the configuration key to set value for.
        :param value:             the value to set.
        :param config_file:       the file to save configurations to.
        :raise KeyError:          if the provided key is not valid.
        :raise PermissionError:   if it fails to write to the config file.
        :raise FileNotFoundError: if it failed to create the config file because its directory
                                  does not exist.
        """
        previous_value = self[key]

        try:
            self[key] = value
            self.save(config_file)

        except (FileNotFoundError, PermissionError, OSError):
            self[key] = previous_value
            raise
