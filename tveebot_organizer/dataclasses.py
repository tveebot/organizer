from typing import NamedTuple

TVShow = NamedTuple('TVShow', [
    ('name', str)
])

Episode = NamedTuple('Episode', [
    ('tvshow', TVShow),
    ('season', int),
    ('number', int),
])
