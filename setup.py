from setuptools import setup, find_packages

setup(
    name='episode-organizer',
    version='0.1',
    description='Tool to organize video files corresponding to TV Shows',
    url='https://github.com/tveebot/organizer',
    license='MIT',
    author='david',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(),

    package_data={
        'tveebot_organizer': ['config.ini'],
    },

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'tveebot-organizerd=tveebot_organizer.daemon:main',
        ],
    },

)
