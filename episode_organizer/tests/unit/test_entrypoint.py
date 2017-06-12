
# TODO config file provided does not exist but directory exists - OK
# TODO config file provided does not exist and directory does not exist - not OK
# TODO invalid ip address
# TODO invalid port (number is too high, is not a number)
import pytest

from episode_organizer import EntryPoint


class TestEntryPoint:

    def test_SetupConfigurator_ConfigDefinesLocalhostAndPort35121_NoErrorIsRaised(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '35121'

        entrypoint.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesLocalhostIpAndPort35121_NoErrorIsRaised(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = '127.0.0.1'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '35121'

        entrypoint.setup_configurator()

    def test_SetupConfigurator_ConfigDefinesInvalidAddress_RaisesValueError(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = 'invalid:address'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '35121'

        with pytest.raises(ValueError) as exception_info:
            entrypoint.setup_configurator()

        assert str(exception_info.value) == "The address 'invalid:address' is not a valid ip or hostname"

    def test_SetupConfigurator_ConfigDefinesPortHigherThan65535_RaisesValueError(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '65536'

        with pytest.raises(ValueError) as exception_info:
            entrypoint.setup_configurator()

        assert str(exception_info.value) == "The port '65536' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortLowerThan1_RaisesValueError(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '0'

        with pytest.raises(ValueError) as exception_info:
            entrypoint.setup_configurator()

        assert str(exception_info.value) == "The port '0' is not valid"

    def test_SetupConfigurator_ConfigDefinesPortIsNotANumber_RaisesValueError(self):

        entrypoint = EntryPoint()
        entrypoint.config['DEFAULT']['ConfiguratorAddress'] = 'localhost'
        entrypoint.config['DEFAULT']['ConfiguratorPort'] = '655dd'

        with pytest.raises(ValueError):
            entrypoint.setup_configurator()
