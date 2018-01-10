from typing import NamedTuple


class TVShow(NamedTuple):
    name: str


class Episode(NamedTuple):
    tvshow: TVShow
    season: int
    number: int
