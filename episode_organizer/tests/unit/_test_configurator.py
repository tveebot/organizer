from contextlib import contextmanager
from unittest.mock import MagicMock, mock_open, patch

import pytest

from episode_organizer.daemon._configurator import Configurator
from episode_organizer.daemon.configuration import Configuration


# noinspection PyTypeChecker
class TestConfigurator:

    @contextmanager
    def stub_out_open(self):
        with patch('episode_organizer.daemon.configuration.open', mock_open()):
            yield

    def test_SetWatchDir_ToExistingDir_WatchDirWasSetToNewDir(self, tmpdir):

        new_watch_dir = tmpdir.mkdir("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict("config.ini", {
                'WatchDirectory': "/watch/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            configurator.set_config('WatchDirectory', str(new_watch_dir))

            assert configurator.get_config('WatchDirectory') == str(new_watch_dir)

    def test_SetWatchDir_ToExistingDir_OrganizerWasInformedOfTheChange(self, tmpdir):

        new_watch_dir = tmpdir.mkdir("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict("config.ini", {
                'WatchDirectory': "/watch/dir"
            })
            organizer_mock = MagicMock()
            configurator = Configurator(configuration, organizer_mock)

            configurator.set_config('WatchDirectory', str(new_watch_dir))

            organizer_mock.set_watch_dir.assert_called_once_with(str(new_watch_dir))

    def test_SetWatchDir_ToNonExistingDir_WatchDirWasKept(self, tmpdir):

        new_watch_dir = tmpdir.join("new_watch")

        with self.stub_out_open():

            configuration = Configuration.from_dict("config.ini", {
                'WatchDirectory': "/watch/dir"
            })
            configurator = Configurator(configuration, organizer=MagicMock())

            with pytest.raises(FileNotFoundError):
                configurator.set_config('WatchDirectory', str(new_watch_dir))

            assert configurator.get_config('WatchDirectory') == "/watch/dir"
