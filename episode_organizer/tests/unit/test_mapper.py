import pytest

from episode_organizer.episode import Episode
from episode_organizer.mapper import Mapper
from episode_organizer.tvshow import TVShow


class TestMapper:

    @pytest.mark.parametrize("name, expected_episode", [
        ("Prison.Break.S05E09.720p.HDTV.x264-KILLERS[rarbg]", Episode(TVShow("Prison Break"), season=5, number=9)),
        ("Castle.2009.S08E22.HDTV.x264-KILLERS[rarbg]", Episode(TVShow("Castle 2009"), season=8, number=22)),
        ("Prison.Break.S1E1", Episode(TVShow("Prison Break"), season=1, number=1)),
    ])
    def test_correct(self, name, expected_episode):

        assert Mapper().map_to_episode(name) == expected_episode

    @pytest.mark.parametrize("name", [
        "Prison.Break.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE1.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SaEa.1720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E720p.HDTV.x264-KILLERS[rarbg]",
    ])
    def test_incorrect(self, name):

        with pytest.raises(ValueError) as exception_info:
            Mapper().map_to_episode(name)

        assert str(exception_info.value) == "The name '%s' did not map to an episode" % name
