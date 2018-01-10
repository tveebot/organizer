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
    - TV Show Name S01E02
    - TV Show Name 1x02

    All of these examples correspond to Episode("TV Show Name", season=1, number=2)
    """

    # List of valid patterns to specify the episode's season and number
    _episode_patterns = [
        "[Ss](?P<season>\d+)x?[Ee](?P<number>\d+)",
        "(?P<season>\d+)x(?P<number>\d+)",
    ]
    _patterns = [re.compile("\w[. ]" + pattern + "([. \-]|\Z)") for pattern in _episode_patterns]

    def match(self, name: str) -> Episode:
        """
        Takes an episode name, parses it, and returns the corresponding episode object.

        The format of the episode name must follow the list of support formats specified in the
        *Matcher*'s class documentation.

        :raise ValueError: if it can not match *name* to an episode
        """
        # Search for a valid episode pattern in the name
        match = None
        for pattern in self._patterns:
            match = pattern.search(name)
            if match:
                break

        if not match:
            raise ValueError("could not match name '%s' to an episode" % name)

        # Use the character before the season number as the word separation character (it could
        # be either a '.' or a ' ')
        separation_char = name[match.start() + 1]

        # The name of the TV show is composed of the words to the left of the season number
        tvshow_name = name[:match.start() + 1]
        # Replace separators with spaces
        tvshow_name = tvshow_name.replace(separation_char, " ")
        # The TV show name is always in title format
        tvshow_name = tvshow_name.title()

        season = int(match.group('season'))
        number = int(match.group('number'))

        return Episode(TVShow(tvshow_name), season, number)
