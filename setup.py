from setuptools import setup, find_packages

setup(
    name='episode-organizer',
    version='0.1',
    description='Tool to organize video files corresponding to TV Shows',
    url='https://github.com/davidfialho14/episode_organizer',
    license='MIT',
    author='david',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(exclude=['episode_organizer.daemon.tests',
                                    'episode_organizer.daemon.tests.integration',
                                    'episode_organizer.daemon.tests.unit']),

    install_requires=['watchdog', 'docopt', 'bidict'],

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'episode-organizer-daemon=episode_organizer.daemon:main',
            'episode-organizer-cli=episode_organizer.config_client:main',
        ],
    },

    package_data={
        'episode_organizer': ['default.ini'],
    },

)
