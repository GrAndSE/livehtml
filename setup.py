#!/usr/bin/env python
"""
Live HTML
=========

Simple tool that helps you to desing in the browser. You just need python
interpreter:

    >>> import livehtml
    >>> livehtml.start_server('.')

Now you can just open your favorite text editor or IDE, create new html file,
write something like:

    <!doctype html>
    <html>
        <head></head>
        <body></body>
    </html>

in this file and open it in browser like:

    http://127.0.0.1:8888/new-file.html

And after any changes you'l save in your file you can immediately see the
changes in browser.
"""
from distutils.core import setup

setup(
    name='livehtml',
    version='0.0.1',
    description='Simple development server for writing an html pages',
    long_description=__doc__,
    keywords='HTML css javascript server',
    author='Andrey Grygoryev',
    author_email='undeadgrandse@gmail.com',
    license='BSD',
    url='https://github.com/GrAndSE/livehtml',
    packages=['livehtml'],
    data_files=[('livehtml', ['livehtml/ldws.js'])],
    platforms="any",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',       
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    requires=['tornado (>=2.2)'],
)
