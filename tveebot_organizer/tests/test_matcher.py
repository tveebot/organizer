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
        ("prison.break.s01e01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.S01e01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.s01E01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.S01xE01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.s01xe01", Episode(TVShow("Prison Break"), season=1, number=1)),
        ("prison.break.01x02", Episode(TVShow("Prison Break"), season=1, number=2)),
        ("prison.break.1x02", Episode(TVShow("Prison Break"), season=1, number=2)),
        ("prison.break.1x2", Episode(TVShow("Prison Break"), season=1, number=2)),
        ("prison.break.1x12", Episode(TVShow("Prison Break"), season=1, number=12)),
        ("prison break 1x12", Episode(TVShow("Prison Break"), season=1, number=12)),
        ("A.S01E02", Episode(TVShow("A"), season=1, number=2)),
        ("A S01E02", Episode(TVShow("A"), season=1, number=2)),
        ("Prison Break S01E02", Episode(TVShow("Prison Break"), season=1, number=2)),
        ("Mr. Robot S01E02", Episode(TVShow("Mr. Robot"), season=1, number=2)),
        ("Mr. Robot 1x02", Episode(TVShow("Mr. Robot"), season=1, number=2)),
        ("Prison Break S01E02-S01E03", Episode(TVShow("Prison Break"), season=1, number=2)),
    ])
    def test_valid_names(self, name, expected_episode):
        assert Matcher().match(name) == expected_episode

    @pytest.mark.parametrize("name", [
        "Prison.Break.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SE1.720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.SaEa.1720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.S1E720p.HDTV.x264-KILLERS[rarbg]",
        "Prison.Break.11",
        "Prison.Break.S1x01",
        "Prison.Break.1xE01",
        "S01E01",
        "AS01E01",
        ".S01E01",
        " S01E01",
        "Prison BreakS01E01",
        "Prison Break1x01",
    ])
    def test_invalid_names(self, name):
        with pytest.raises(ValueError):
            print(Matcher().match(name))
