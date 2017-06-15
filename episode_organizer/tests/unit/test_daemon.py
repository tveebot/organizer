from unittest.mock import patch

import pytest

from episode_organizer.daemon import Daemon
from episode_organizer.daemon.configuration import Configuration


class TestDaemon:

    @pytest.fixture(autouse=True)
    def mock_default_user_config_file(self, tmpdir):
        Daemon.DEFAULT_USER_CONFIG_FILE = str(tmpdir.join("default_user.ini"))

    def test_LoadConfigs_UserProvidesExistingFile_DaemonUsesUserFile(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        daemon = Daemon()

        daemon.load_configurations(user_config_file=str(config_file))

        assert daemon.config_file == str(config_file)

    def test_LoadConfigs_UserProvidesNonExistingFile_DaemonUsesUserFile(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        daemon = Daemon()

        daemon.load_configurations(user_config_file=str(config_file))

        assert daemon.config_file == str(config_file)

    def test_LoadConfigs_UserDoesNotProvideConfigFile_DaemonUsesDefaultUserFile(self):

        daemon = Daemon()
        daemon.load_configurations(user_config_file=None)

        assert daemon.config_file == daemon.DEFAULT_USER_CONFIG_FILE

    @patch('episode_organizer.daemon.daemon.os.makedirs')
    def test_LoadConfigs_UserDefaultConfigDirCannotBeCreatedDueToOSError_RaisesOSError(self, makedirs_stub, tmpdir):

        makedirs_stub.side_effect = OSError()

        with pytest.raises(OSError):
            Daemon().load_configurations(user_config_file=None)

    @patch('episode_organizer.daemon.daemon.fileConfig')
    def test_SetupLoggers_UserProvidesExistingFile_DaemonUsesUserFile(self, fileConfig_mock, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        daemon = Daemon()

        daemon.setup_loggers(logs_config_file=str(config_file))

        fileConfig_mock.assert_called_once_with(str(config_file))

    @patch('episode_organizer.daemon.daemon.fileConfig')
    def test_SetupLoggers_UserProvidesNonExistingFile_RaisesFileNotFoundError(self, fileConfig_mock, tmpdir):

        config_file = tmpdir.join("config.ini")
        daemon = Daemon()

        with pytest.raises(FileNotFoundError):
            daemon.setup_loggers(logs_config_file=str(config_file))

    @patch('episode_organizer.daemon.daemon.fileConfig')
    def test_SetupLoggers_UserDoesNotProvideConfigFile_DaemonUsesDefaultFile(self, fileConfig_mock):

        daemon = Daemon()
        daemon.setup_loggers(logs_config_file=None)

        fileConfig_mock.assert_called_once_with(str(Configuration.default_config_file))

    def test_SetupOrganizer_WatchDirectoryDoesNotExist_RaisesFileNotFoundError(self, tmpdir):

        daemon = Daemon()
        daemon.config['WatchDirectory'] = str(tmpdir.join("watch"))
        daemon.config['StorageDirectory'] = str(tmpdir.mkdir("storage"))

        with pytest.raises(FileNotFoundError) as exception_info:
            daemon.setup_organizer()

        assert str(exception_info.value) == "Watch directory does not exist: %s" % str(tmpdir.join("watch"))

    def test_SetupOrganizer_StorageDirectoryDoesNotExist_RaisesFileNotFoundError(self, tmpdir):

        daemon = Daemon()
        daemon.config['WatchDirectory'] = str(tmpdir.mkdir("watch"))
        daemon.config['StorageDirectory'] = str(tmpdir.join("storage"))

        with pytest.raises(FileNotFoundError) as exception_info:
            daemon.setup_organizer()

        assert str(exception_info.value) == "Storage directory does not exist: %s" % str(tmpdir.join("storage"))

    def test_SetupConfigurator_ConfigDefinesLocalhostAndPort35121_NoErrorIsRaised(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = 'localhost'
        daemon.config['ConfiguratorPort'] = '35121'

        daemon.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesLocalhostIpAndPort35121_NoErrorIsRaised(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = '127.0.0.1'
        daemon.config['ConfiguratorPort'] = '35121'

        daemon.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesInvalidAddress_RaisesValueError(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = 'invalid:address'
        daemon.config['ConfiguratorPort'] = '35121'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The address 'invalid:address' is not a valid ip or hostname"

    def test_SetupConfigurator_ConfigDefinesPortHigherThan65535_RaisesValueError(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = 'localhost'
        daemon.config['ConfiguratorPort'] = '65536'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The port '65536' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortLowerThan1_RaisesValueError(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = 'localhost'
        daemon.config['ConfiguratorPort'] = '0'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The port '0' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortIsNotANumber_RaisesValueError(self):

        daemon = Daemon()
        daemon.config['ConfiguratorAddress'] = 'localhost'
        daemon.config['ConfiguratorPort'] = '655dd'

        with pytest.raises(ValueError) as exception_info:
            daemon.setup_configurator()

        assert str(exception_info.value) == "The port '655dd' is not valid"
