import re

from show_organizer.episode import Episode
from show_organizer.tvshow import TVShow


class Mapper:
    """
    Mapper is one of the central components. Its job is to take a string and obtain the episode information from that
    string. This string can't be any string is expected have a format similar to 'TV.Show.Name.S01E02.720p',
    where the substring 'TV.Show.Name' indicates the name of the episode's tv show and 'S01E02' indicates that the
    episode is the second of season 1. This string is provided by the organizer.
    """

    # An episode pattern corresponds to a 'word' of the form S01E01
    # Where S01 indicates the episode corresponds to season 1
    # and E01 indicates the episode is the first episode of the season
    episode_pattern = re.compile('S(?P<season>\d+)E(?P<number>\d+)\Z')

    def map_to_episode(self, name: str) -> Episode:
        """
        Maps a name to an episode object. The input name maybe the name of a folder or a file. The name is expected have a
        format similar to 'TV.Show.Name.S01E02.720p', where the substring 'TV.Show.Name' indicates the name of the
        episode's tv show and 'S01E02' indicates that the episode is the second of season 1. Characters to the right of
        'S01E01' are all ignored.

        :param name: name to be parsed and mapped to an episode.
        :return: the episode corresponding to the given name.
        :raise ValueError: if the name can not be mapped to an episode.
        """

        # The character '.' divides words
        # Take each word
        words = name.split('.')

        # Look for an episode pattern
        for index, word in enumerate(words):

            match = self.episode_pattern.match(word)
            if match:
                # The previous words compose the tv show name
                tvshow_name = " ".join(words[:index])

                season = int(match.group('season'))
                number = int(match.group('number'))

                return Episode(TVShow(tvshow_name), season, number)

        raise ValueError("The name '%s' did not map to an episode" % name)
