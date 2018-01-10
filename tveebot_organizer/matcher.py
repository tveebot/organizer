import re

from tveebot_organizer.dataclasses import Episode, TVShow


class Matcher:
    """
    The Matcher is one of the sub-components of the *Organizer*. An organizer is associated with a
    single matcher. The matcher is used to match an episode name, using some pre-defined format,
    to an episode object.

    Supported formats:

    - TV.Show.Name.S01E02
    - TV.Show.Name.s01e02
    - TV.Show.Name.S01xE02
    - TV.Show.Name.1x02

    All of these examples correspond to Episode("TV Show Name", season=1, number=2)

    """

    # List of valid patterns to specify the episode's season and number
    _patterns = [
        re.compile('[Ss](?P<season>\d+)x?[Ee](?P<number>\d+)\Z'),
        re.compile('(?P<season>\d+)x(?P<number>\d+)\Z'),
    ]

    def match(self, name: str) -> Episode:
        """
        Takes an episode name, parses it, and returns the corresponding episode object.

        The format of the episode name must follow the list of support formats specified in the
        *Matcher*'s class documentation.

        :raise ValueError: if it can not match *name* to an episode
        """
        # The character '.' divides words
        # Take each word
        words = name.split('.')

        # Look for an episode pattern
        episode = None
        for index, word in enumerate(words):

            # Try to match word to any pattern, in the order they are specified
            match = None
            for pattern in self._patterns:
                match = pattern.match(word)
                if match:
                    break

            if match:
                # The words before the episode pattern compose the tv show name.
                tvshow_name = " ".join(words[:index])

                # Capitalize the first letter of each word of the tvshow name
                tvshow_name = tvshow_name.title()

                season = int(match.group('season'))
                number = int(match.group('number'))

                episode = Episode(TVShow(tvshow_name), season, number)

        if episode is None:
            raise ValueError("could not match name '%s' to an episode" % name)

        return episode
