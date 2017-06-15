import configparser
from configparser import ConfigParser
from io import StringIO

from unittest.mock import patch
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

    def test_GetValue_ForValidKey_ReturnsCorrespondingValue(self):

        config = Configuration.from_dict({
            'WatchDirectory': "test_watch"
        })

        assert config['WatchDirectory'] == "test_watch"

    def test_GetValue_ForInvalidKey_RaisesKeyError(self):

        config = Configuration.from_dict({
            'WatchDirectory': "test_watch"
        })

        with pytest.raises(KeyError):
            value = config['InvalidKey']

    def test_GetValue_ForValidKeyWithoutADefinedValue_ReturnsDefaultValueForThatKey(self):

        config = Configuration.from_dict({
            'WatchDirectory': "test_watch"
        })

        # StorageDirectory is a valid key but is not defined
        assert config['StorageDirectory'] == defaults.config['StorageDirectory']

    def test_SetValue_ForValidKey_ValueUpdatedForThatKey(self):

        config = Configuration()
        config['WatchDirectory'] = "new_watch"

        assert config['WatchDirectory'] == "new_watch"

    def test_SetValue_ForInvalidKey_RaisesKeyError(self):

        config = Configuration()

        with pytest.raises(KeyError):
            config['InvalidKey'] = "new_watch"

    def test_Load_EmptyConfigFile_UsesDefaultValues(self):

        config_file = StringIO("")

        config = Configuration()
        config.load_file(config_file)

        assert config['WatchDirectory'] == defaults.config['WatchDirectory']

    def test_Load_FileWhichDefinesValuesForAKey_ConfigUsesProvidedValueForThatKey(self):

        config_file = StringIO(
            "[DEFAULT]\n"
            "WatchDirectory = test_watch\n"
        )

        config = Configuration()
        config.load_file(config_file)

        assert config['WatchDirectory'] == "test_watch"

    def test_Load_FileDoesNotExist_RaisesFileNotFoundError(self, tmpdir):

        config = Configuration()

        with pytest.raises(FileNotFoundError):
            config.load(str(tmpdir.join("config.ini")))

    def test_Load_DoesNotHavePermissionToReadFile_RaisesPermissionError(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        config_file.chmod(0o333)

        with pytest.raises(PermissionError):
            Configuration().load(str(config_file))

    def test_Load_FileFormatIsWrong_RaisesConfigParserError(self):

        config_file = StringIO("invalid format\n")

        with pytest.raises(configparser.Error):
            Configuration().load_file(config_file)

    def test_Save_ToExistingFile_FileContainsNewConfigurationsIncludingDefault(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = test_watch\n"
        )
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        config.save(str(config_file))

        assert self.config_file_contains(str(config_file), 'WatchDirectory', 'test_watch')
        assert self.config_file_contains(str(config_file), 'StorageDirectory', defaults.config['StorageDirectory'])

    def test_Save_ToNonExistingFile_FileIsCreatedAndConfigsSaved(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        config.save(str(config_file))

        assert self.config_file_contains(str(config_file), 'WatchDirectory', 'test_watch')

    def test_Save_ToFileDirectoryOfWhichDoesNotExist_RaisesFileNotFoundError(self, tmpdir):

        config_file = tmpdir.join("conf").join("config.ini")
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        with pytest.raises(FileNotFoundError):
            config.save(str(config_file))

    def test_Save_ToExistingFileWithoutWritePermission_RaisesPermissionError(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write("")
        config_file.chmod(0o555)
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        with pytest.raises(PermissionError):
            config.save(str(config_file))

    def test_Save_ToNonExistingFileInDirectoryWithoutWritePermission_RaisesPermissionError(self, tmpdir):

        config_dir = tmpdir.mkdir("conf")
        config_file = config_dir.join("config.ini")
        config_dir.chmod(0o555)
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        with pytest.raises(PermissionError):
            config.save(str(config_file))

    def test_UpdateConfigValue_SavingToExistingFile_ValueIsUpdatedInMemoryAndDisk(self, tmpdir):

        config_file = tmpdir.join("config.ini")
        config_file.write(
            "[DEFAULT]\n"
            "WatchDirectory = test_watch\n"
        )
        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })

        config.update(str(config_file), key='WatchDirectory', value='new_watch')

        assert config['WatchDirectory'] == 'new_watch'
        assert self.config_file_contains(str(config_file), key='WatchDirectory', value='new_watch')

    @patch.object(Configuration, 'save')
    def test_UpdateConfigValue_SaveRaisesFileNotFoundError_RaisesPermissionErrorValueIsNotUpdated(self, save_stub):

        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })
        save_stub.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError):
            config.update("conf/config.ini", key='WatchDirectory', value='new_watch')

        assert config['WatchDirectory'] == 'test_watch'

    @patch.object(Configuration, 'save')
    def test_UpdateConfigValue_SaveRaisesPermissionError_RaisesPermissionErrorValueIsNotUpdated(self, save_stub):

        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })
        save_stub.side_effect = PermissionError()

        with pytest.raises(PermissionError):
            config.update("conf/config.ini", key='WatchDirectory', value='new_watch')

        assert config['WatchDirectory'] == 'test_watch'

    @patch.object(Configuration, 'save')
    def test_UpdateConfigValue_SaveRaisesOSError_RaisesOSErrorValueIsNotUpdated(self, save_stub):

        config = Configuration.from_dict({
            'WatchDirectory': 'test_watch'
        })
        save_stub.side_effect = OSError()

        with pytest.raises(OSError):
            config.update("conf/config.ini", key='WatchDirectory', value='new_watch')

        assert config['WatchDirectory'] == 'test_watch'
