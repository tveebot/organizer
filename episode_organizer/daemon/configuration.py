from configparser import ConfigParser
from contextlib import suppress

from pkg_resources import resource_filename, Requirement


class Configuration:
    """
    The configuration class provides an interface to access and modify the current configurations of the system.
    This class is supposed to work as close to a dictionary as possible.
    """

    default_config_file = resource_filename(
        Requirement.parse("episode_organizer"), 'episode_organizer/daemon/default.ini')

    def __init__(self, config_file):
        """
        Initializes the configurations with the default values from the 'default.ini' file.
        If the provided config file exists then the configurations from that file will be used.
        """
        self.config_file = config_file
        self._config = ConfigParser()
        self._config.read(self.default_config_file)

    def __getitem__(self, key):
        """
        Returns the current value for a configuration key. If the configuration file does not exist, then returns the
        default value for the given key.

        :param key: the configuration key to obtain the value of.
        :return: the value for the given key.
        :raise KeyError: if the given key is invalid.
        :raise OSError:  if it fails to read the config file.
        """
        # Note: should not use read(file) below because this ignores any OS error when trying to read the file
        # Here we do want to ignore FileNotFoundError, but not other OS errors such as permission denied or others.
        # We want to make sure that if the file exists, then we are able to read it.
        with suppress(FileNotFoundError):
            with open(self.config_file) as file:
                self._config.read_file(file)  # do not user read() here (see note above)

        return self._config['DEFAULT'][key]

    def __setitem__(self, key, value):
        """
        Sets a new value for a valid configuration key. Updates the configuration file.

        :param key:                 configuration key to set value for.
        :param value:               value to set.
        :raise KeyError:            if the provided key is not valid.
        :raise OSError:             if it fails to write to the config file.
        :raise FileNotFoundError:   if it failed to create the config file because its directory does not exist.
        """
        if key not in self._config['DEFAULT']:
            raise KeyError("Key '%s' is not a valid" % key)

        self._config['DEFAULT'][key] = value
        self._save()

    def _save(self):

        # Update the configuration file
        with open(self.config_file, "w") as file:
            self._config.write(file)

    @staticmethod
    def from_dict(config_file, config: dict):
        """
        Builds a configuration instance from a dictionary with the configurations. The keys mut be valid, otherwise a
        KeyError will be raised. The configuration is saved to the provided file. If the dictionary does not defines
        some configuration parameter, then the default one is used.

        :param config_file: the file to save configurations to.
        :param config:      the dictionary defining the configurations.
        :return: a new configuration instance initialized with the configurations provided in the dictionary.
        """
        configuration = Configuration(config_file)

        for key, value in config.items():

            if key not in configuration._config['DEFAULT']:
                raise KeyError("Key '%s' is not a valid" % key)

            configuration._config['DEFAULT'][key] = value

        configuration._save()
        return configuration
