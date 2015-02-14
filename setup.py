# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='wiring',
    version='1.0.0',
    description='Architectural foundation for Python applications.',
    long_description=long_description,
    url='https://github.com/msiedlarek/wiring',
    author=u'Mikołaj Siedlarek',
    author_email='mikolaj@siedlarek.pl',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='wiring dependency injection',
    install_requires=[
        'six',
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    packages=[
        'wiring',
    ],
    package_dir={
        'wiring': 'wiring',
    },
    package_data={
        '': ['LICENSE'],
    },
    include_package_data=True
)
