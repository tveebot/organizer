import pytest

from tveebot_organizer.dataclasses import Episode, TVShow
from tveebot_organizer.matcher import Matcher


class TestMatcher:

    @pytest.mark.parametrize("name, expected_episode", [
        ("Prison.Break.S05E09.720p.x264-KRS", Episode(TVShow("Prison Break"), season=5, number=9)),
        ("Castle.2009.S08E22.x264-KILS[rg]", Episode(TVShow("Castle 2009"), season=8, number=22)),
        ("Prison.Break.S1E1", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.S01E01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("PRison.BrEAk.S01E01", Episode(TVShow("Prison Break"), season=1, number=1)),
    ])
    def test_valid_names(self, name, expected_episode):
        assert Matcher().map_to_episode(name) == expected_episode

    @pytest.mark.parametrize("name", [
        "Prison.Break.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE1.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SaEa.1720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E720p.HDTV.x264-KILLERS[rarbg]",
    ])
    def test_invalid_names(self, name):
        with pytest.raises(ValueError):
            Matcher().map_to_episode(name)
