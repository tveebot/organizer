import re

from show_organizer.episode import Episode

# An episode pattern corresponds to a 'word' of the form S01E01
# Where S01 indicates the episode corresponds to season 1
# and E01 indicates the episode is the first episode of the season
from show_organizer.tvshow import TVShow

episode_pattern = re.compile("S(?P<season>\\d+)E(?P<number>\\d+)")


def map_to_episode(name: str) -> Episode:

    # The character '.' divides words
    # Take each word
    words = name.split('.')

    # Look for an episode pattern
    for index, word in enumerate(words):

        match = episode_pattern.match(word)
        if match:
            # The previous words compose the tv show name
            tvshow_name = " ".join(words[:index])

            season = int(match.group('season'))
            number = int(match.group('number'))

            return Episode(TVShow(tvshow_name), season, number)

    raise ValueError("The name '%s' did not map to an episode" % name)
