from collections import namedtuple

TVShow = namedtuple('TVShow', 'name')
Episode = namedtuple('Episode', 'tvshow, season, number')
