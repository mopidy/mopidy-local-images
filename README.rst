Mopidy-Local-Images
========================================================================

Mopidy-Local-Images is a Mopidy_ local library extension that allows
Web clients access to album art embedded in local media files.  It
does so by acting as a *proxy* between Mopidy's ``local scan`` command
and the actual local library provider being used.  Images are
extracted from media files and stored separately while scanning, and
corresponding image URIs are inserted into Mopidy data models, so
clients can access these images through Mopidy's integrated Web
server.  Other requests are delegated to the actual local library
provider as-is.

Album art stored in separate files is also supported.  External image
files will be considered if they reside in the same directory as the
scanned media files, and file names match a configurable pattern.

Please note, however, that support for local album art depends on
whether your client supports album image URIs as provided by Mopidy's
data model.  For example, `some clients`_ still ignore any images
provided by this extension, and will try to retrieve matching album
art from external services instead.


Installation
------------------------------------------------------------------------

Mopidy-Local-Images can be installed using pip_ by running::

    pip install Mopidy-Local-Images


Configuration
------------------------------------------------------------------------

Before starting Mopidy, you must change your configuration to switch
to using Mopidy-Local-Images as your local library provider::

    [local]
    library = images

By default, Mopidy-Local-Images delegates any requests to the standard
``json`` local library provider.  To use a third-party library, such
as `Mopidy-Local-SQLite`_, you have to set this in the
``local-images`` configuration section::

    [local-images]
    library = sqlite

Once this has been set, you need to clear and re-scan your library for
images to be extracted::

    mopidy local clear
    mopidy local scan

This extension also provides some other configuration settings, but
beware that these are subject to change for now::

    [local-images]
    enabled = true

    # the actual local library provider to use
    library = json

    # base URI for images; change this if you want to serve images using
    # an alternative Web server
    base_uri = /images/

    # directory where local image files are stored; if not set, defaults
    # to a subdirectory of `local/data_dir`
    image_dir =

    # list of file names to check for when searching for external album
    # art; may contain UNIX shell patterns, i.e. "*", "?", etc.
    album_art_files = *.jpg, *.jpeg, *.png


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/Mopidy-Local-Images.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Local-Images/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/Mopidy-Local-Images.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Local-Images/
    :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/tkem/mopidy-local-images/master.svg?style=flat
    :target: https://travis-ci.org/tkem/mopidy-local-images/
    :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/tkem/mopidy-local-images/master.svg?style=flat
   :target: https://coveralls.io/r/tkem/mopidy-local-images/
   :alt: Test coverage

- `Issue Tracker`_
- `Source Code`_
- `Change Log`_


License
------------------------------------------------------------------------

Copyright (c) 2014 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


Known Bugs and Limitations
------------------------------------------------------------------------

Using this extension will slow down ``mopidy local scan``
considerably, since every media file added has to be scanned twice.
This is a limitation of the Mopidy local library provider interface.


.. _Mopidy: http://www.mopidy.com/
.. _some clients: https://github.com/martijnboland/moped/issues/17

.. _pip: https://pip.pypa.io/en/latest/

.. _Mopidy-Local-SQLite: https://pypi.python.org/pypi/Mopidy-Local-SQLite/

.. _Issue Tracker: https://github.com/tkem/mopidy-local-images/issues/
.. _Source Code: https://github.com/tkem/mopidy-local-images/
.. _Change Log: https://github.com/tkem/mopidy-local-images/blob/master/CHANGES.rst

.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
