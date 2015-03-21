# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='guestbook',
    version='1.0.0',
    description='Simple example of Wiring used in a web application.',
    long_description=long_description,
    url='https://github.com/msiedlarek/wiring/tree/master/example',
    author=u'Mikołaj Siedlarek',
    author_email='mikolaj@siedlarek.pl',
    license='Apache License, Version 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'wiring',
        'werkzeug==0.10.1',
        'jinja2==2.7.3',
    ],
    entry_points={
        'console_scripts': [
            'guestbook-serve = guestbook.wsgi:serve',
        ],
    }
)
