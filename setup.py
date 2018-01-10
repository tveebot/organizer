from setuptools import setup, find_packages

setup(
    name='episode-organizer',
    version='0.2',
    description='Tool to organize video files corresponding to TV Shows',
    url='https://github.com/tveebot/organizer',
    license='MIT',
    author='david',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(),

    package_data={
        'episode_organizer.daemon': ['default.ini'],
        'tveebot_organizer': ['config.ini'],
    },

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'episode-organizer-daemon=episode_organizer.daemon:main',
            'episode-organizer-cli=episode_organizer.config_client:main',
            'tveebot-organizerd=tveebot_organizer.daemon:main',
        ],
    },

)
