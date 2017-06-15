import configparser

import pytest

from episode_organizer.daemon import Daemon


class TestDaemon:

    def test_LoadConfigs_ConfigFileExistsButItsEmpty_Accept(self, tmpdir):
        tmpdir.mkdir("conf")
        config_file = tmpdir.join("conf").join("config.ini")
        config_file.write("")

        daemon = Daemon()
        daemon.load_configurations(str(config_file))

    def test_LoadConfigs_ConfigFileDoesNotExistButItsDirectoryDoesExist_Accept(self, tmpdir):
        tmpdir.mkdir("conf")

        daemon = Daemon()
        daemon.load_configurations(config_file=str(tmpdir.join("conf").join("config.ini")))

    def test_LoadConfigs_DirectoryOfConfigFileDoesNotExist_RaiseFileNotFoundError(self, tmpdir):
        daemon = Daemon()
        daemon.load_configurations(config_file=str(tmpdir.join("conf").join("config.ini")))

    def test_LoadConfigs_ConfigFileHasWrongFormat_RaiseConfigParserError(self, tmpdir):
        tmpdir.mkdir("conf")
        config_file = tmpdir.join("conf").join("config.ini")
        config_file.write("olasdasd")

        daemon = Daemon()

        with pytest.raises(configparser.Error):
            daemon.load_configurations(str(config_file))

    @pytest.fixture
    def default_config_file(self, tmpdir):

        default_config_file = tmpdir.join("default.init")
        default_config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = default_watch/\n"
            "StorageDirectory = default_storage/\n"
            "ConfiguratorAddress = default_localhost\n"
            "ConfiguratorPort = 35121\n"
        )

        return str(default_config_file)

    def test_LoadConfigs_UserDoesNotProvideConfigFile_UsesDefaultConfigurations(self, default_config_file):
        daemon = Daemon()
        daemon.default_config_file = default_config_file

        daemon.load_configurations(config_file=None)

        # Here we check only one of the parameters
        assert daemon.config['DEFAULT']['WatchDirectory'] == 'default_watch/'

    def test_LoadConfigs_UserDoesNotProvideConfigFile_ConfigFileIsSetToDefaultUserConfigFile(self, default_config_file):
        daemon = Daemon()
        daemon.default_config_file = default_config_file

        daemon.load_configurations(config_file=None)

        assert daemon.config_file == daemon.DEFAULT_USER_CONFIG_FILE

    def test_LoadConfigs_UserProvidesConfigFile_ConfigurationsInUserFileOverrideDefault(
            self, default_config_file, tmpdir):

        daemon = Daemon()
        daemon.default_config_file = default_config_file

        tmpdir.mkdir("conf")
        config_file = tmpdir.join("conf").join("config.ini")
        # Note user only defines the values for 'WatchDirectory' and 'StorageDirectory'
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = user_watch/\n"
            "StorageDirectory = user_storage/\n"
        )

        daemon.load_configurations(config_file=str(config_file))

        assert daemon.config['DEFAULT']['WatchDirectory'] == 'user_watch/'

    def test_LoadConfigs_UserProvidesConfigFile_ParametersNotDefinedInUserAreSetToDefaultValues(
            self, default_config_file, tmpdir):

        daemon = Daemon()
        daemon.default_config_file = default_config_file

        tmpdir.mkdir("conf")
        config_file = tmpdir.join("conf").join("config.ini")
        # Note user only defines the values for 'WatchDirectory' and 'StorageDirectory'
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = user_watch/\n"
            "StorageDirectory = user_storage/\n"
        )

        daemon.load_configurations(config_file=str(config_file))

        assert daemon.config['DEFAULT']['ConfiguratorAddress'] == 'default_localhost'

    def test_SetupOrganizer_WatchDirectoryDoesNotExist(self, tmpdir):

        daemon = Daemon()
        daemon.config['DEFAULT']['WatchDirectory'] = str(tmpdir.join("watch"))
        daemon.config['DEFAULT']['StorageDirectory'] = str(tmpdir.mkdir("storage"))

        with pytest.raises(FileNotFoundError) as exception_info:
            daemon.setup_organizer()

        assert str(exception_info.value) == "Watch directory does not exist: %s" % str(tmpdir.join("watch"))

    def test_SetupOrganizer_StorageDirectoryDoesNotExist(self, tmpdir):
        daemon = Daemon()
        daemon.config['DEFAULT']['WatchDirectory'] = str(tmpdir.mkdir("watch"))
        daemon.config['DEFAULT']['StorageDirectory'] = str(tmpdir.join("storage"))

        with pytest.raises(FileNotFoundError) as exception_info:
            daemon.setup_organizer()

        assert str(exception_info.value) == "Storage directory does not exist: %s" % str(tmpdir.join("storage"))

    def test_SetupConfigurator_ConfigDefinesLocalhostAndPort35121_NoErrorIsRaised(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '35121'

        daemon.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesLocalhostIpAndPort35121_NoErrorIsRaised(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = '127.0.0.1'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '35121'

        daemon.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesInvalidAddress_RaisesValueError(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = 'invalid:address'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '35121'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The address 'invalid:address' is not a valid ip or hostname"

    def test_SetupConfigurator_ConfigDefinesPortHigherThan65535_RaisesValueError(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '65536'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The port '65536' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortLowerThan1_RaisesValueError(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '0'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The port '0' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortIsNotANumber_RaisesValueError(self):
        daemon = Daemon()
        daemon.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        daemon.config['DEFAULT']['ConfiguratorPort'] = '655dd'

        with pytest.raises(ValueError):
            daemon.setup_configurator()
