from configparser import ConfigParser

import pytest

from episode_organizer.daemon.configuration import Configuration
from episode_organizer.tests import defaults


class TestConfiguration:

    @staticmethod
    def config_file_contains(config_file, key, value):
        config = ConfigParser()
        config.read(config_file)

        try:
            current_value = config['DEFAULT'][key]
            return current_value == value

        except KeyError:
            return False

    def test_GetValidKey_ReturnsCorrespondingValue(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )

        config = Configuration(str(config_file))

        assert config['WatchDirectory'] == "my_watch"

    def test_GetInvalidValidKey_ReturnsKeyError(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )

        config = Configuration(str(config_file))

        with pytest.raises(KeyError):
            assert config['InvalidKey'] == "my_watch"

    def test_GetValidKey_ConfigFileDoesNotContainThatKey_ReturnsDefaultValue(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )

        config = Configuration(str(config_file))

        assert config['StorageDirectory'] == defaults.config['StorageDirectory']

    def test_GetKey_ConfigFileDoesNotExist_ReturnDefaultValue(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config = Configuration(str(config_file))

        assert config['WatchDirectory'] == defaults.config['WatchDirectory']

    def test_SetValueToValidKey_ConfigFileExistsAndContainsKey_ConfigurationAndConfigFileAreUpdated(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )
        config = Configuration(str(config_file))

        config['WatchDirectory'] = 'new_my_watch'

        assert self.config_file_contains(str(config_file), 'WatchDirectory', 'new_my_watch')
        assert config['WatchDirectory'] == 'new_my_watch'

    def test_SetValueToValidKey_ConfigFileExistsButDoesNotContainsKey_KeyAndValueAreAddedToConfigFileIs(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )
        config = Configuration(str(config_file))

        config['StorageDirectory'] = 'my_storage'

        assert self.config_file_contains(str(config_file), 'StorageDirectory', 'my_storage')
        assert config['StorageDirectory'] == 'my_storage'

    def test_SetValueToValidKey_ConfigFileDoesNotExist_ConfigFileCreatedWithKeyAndValueSet(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config = Configuration(str(config_file))

        config['WatchDirectory'] = 'my_watch'

        assert self.config_file_contains(str(config_file), 'WatchDirectory', 'my_watch')
        assert config['WatchDirectory'] == 'my_watch'

    def test_SetValueToInvalidValidKey_RaisesKeyError(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config = Configuration(str(config_file))

        with pytest.raises(KeyError):
            config['InvalidKey'] = 'some value'

    def test_SetValueToValidKey_DirectoryContainingConfigFileDoesNotExist_RaisesFileNotFoundErrorAndConfigNotChanged(
            self, tmpdir):

        config_file = tmpdir.join("some dir").join("config.ini")
        config = Configuration(str(config_file))
        previous_value = defaults.config['WatchDirectory']

        with pytest.raises(FileNotFoundError):
            config['WatchDirectory'] = 'my_watch'

        assert config['WatchDirectory'] == previous_value

    def test_GetValueToValidKey_NoPermissionToReadConfigFile_RaisesOSError(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = my_watch\n"
        )
        config_file.chmod(mode=0o333)
        config = Configuration(str(config_file))

        with pytest.raises(PermissionError):
            value = config['WatchDirectory']

    def test_SetValueToValidKey_NoPermissionToWriteToConfigFile_RaisesPermissionErrorAndConfigNotChanged(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        config_file.chmod(mode=0o555)
        config = Configuration(str(config_file))
        previous_value = defaults.config['WatchDirectory']

        with pytest.raises(PermissionError):
            config['WatchDirectory'] = 'my_watch'

        assert config['WatchDirectory'] == previous_value

    def test_SetValueToValidKey_NoPermissionToWriteToConfigFileDirectory_RaisesPermissionErrorAndConfigNotChanged(
            self, tmpdir):

        config_dir = tmpdir.mkdir("conf")
        config_dir.chmod(mode=0o555)
        config_file = config_dir.join("config.ini")
        config = Configuration(str(config_file))
        previous_value = defaults.config['WatchDirectory']

        with pytest.raises(PermissionError):
            config['WatchDirectory'] = 'my_watch'

        assert config['WatchDirectory'] == previous_value
