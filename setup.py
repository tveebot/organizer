from setuptools import setup, find_packages

setup(
    name='tveebot-organizer',
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

    install_requires=['docopt==0.6.2', 'watchdog==0.8.3'],

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'tveebot-organizer=tveebot_organizer.daemon:main',
        ],
    },

)
