from __future__ import unicode_literals

from setuptools import setup, find_packages


def get_version(filename):
    import re
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-Local-Images',
    version=get_version('mopidy_local_images/__init__.py'),
    url='https://github.com/tkem/mopidy-local-images',
    license='Apache License, Version 2.0',
    author='Thomas Kemmer',
    author_email='tkemmer@computer.org',
    description='Mopidy local library proxy extension for handling embedded album art',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 0.19',
        'uritools >= 0.10'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'local-images = mopidy_local_images:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
