from setuptools import setup, find_packages

setup(
    name='show_organizer',
    version='v0.1',
    description='Tool to organize video files corresponding to TV Shows',
    url='https://github.com/davidfialho14/show_organizer',
    license='MIT',
    author='david',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(exclude=['tests']),

    extras_require={
        'test': ['pytest'],
    },

)
