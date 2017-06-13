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

    install_requires=['watchdog', 'docopt'],

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'episode-organizer=episode_organizer:main',
        ],
    },

    package_data={
        'episode_organizer': ['default.ini'],
    },

)
