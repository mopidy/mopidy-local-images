from __future__ import unicode_literals

import hashlib
import os
import shutil
import tempfile
import unittest

import mock

from mopidy import local
from mopidy.audio import scan
from mopidy.models import Album, Track
from mopidy_local_images import library

GIF_DATA = """
R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
""".decode('base64')

# setup mock local library
mock_library = mock.MagicMock(local.Library)
mock_library.configure_mock(name='mock')
mock_library.return_value = mock_library
library.ImageLibrary.libraries = [mock_library]


class LocalLibraryProviderTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.library = library.ImageLibrary({
            'local': {
                'media_dir': self.tempdir,
                'scan_timeout': 0
            },
            'local-images': {
                'library': 'mock',
                'base_uri': '/images/',
                'image_dir': self.tempdir,
                'album_art_files': []
            }
        })

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_add(self):
        track = Track(name='Foo', uri=b'local:track:foo.mp3')

        mock_library.add_supports_tags_and_duration = False
        self.library.add(track)
        mock_library.add.assert_called_with(track)

        mock_library.add_supports_tags_and_duration = True
        self.library.add(track)
        mock_library.add.assert_called_with(track, None, None)

    def test_add_with_tags_and_duration(self):
        track = Track(name='Foo', uri=b'local:track:foo.mp3')

        self.assertTrue(self.library.add_supports_tags_and_duration)

        mock_library.add_supports_tags_and_duration = False
        self.library.add(track, {'tag': 'bar'}, 0)
        mock_library.add.assert_called_with(track)

        mock_library.add_supports_tags_and_duration = True
        self.library.add(track, {'tag': 'bar'}, 0)
        mock_library.add.assert_called_with(track, {'tag': 'bar'}, 0)

    def test_load(self):
        self.library.load()
        mock_library.load.assert_called_with()

    def test_browse(self):
        self.library.browse(b'local:directory')
        mock_library.browse.assert_called_with(b'local:directory')

    @unittest.skipUnless(hasattr(mock_library, 'get_distinct'), 'Mopidy v0.20')
    def test_get_distinct(self):
        self.library.get_distinct('album')
        mock_library.get_distinct.assert_called_with('album', None)

    @unittest.skipUnless(hasattr(mock_library, 'get_images'), 'Mopidy v0.20')
    def test_get_images(self):
        self.library.get_images([b'local:track:foo.mp3'])
        mock_library.get_images.assert_called_with([b'local:track:foo.mp3'])
        pass

    def test_lookup(self):
        self.library.lookup(b'local:track:foo.mp3')
        mock_library.lookup.assert_called_with(b'local:track:foo.mp3')

    def test_search(self):
        self.library.search({})
        mock_library.search.assert_called_with({}, 100, 0, None, False)

    @mock.patch.object(scan.Scanner, 'scan')
    def test_scan(self, mock_scan):
        album = Album(name='foo')
        track = Track(uri=b'local:track:foo.mp3', album=album)
        path = hashlib.md5(GIF_DATA).hexdigest() + '.gif'
        image_track = track.copy(album=album.copy(images=['/images/' + path]))

        mock_scan.return_value = {'tags': {'image': [GIF_DATA]}}

        self.library.add(track)
        mock_library.add.assert_called_with(image_track, None, None)
        self.assertTrue(os.path.isfile(os.path.join(self.tempdir, path)))

        self.library.close()
        self.assertFalse(os.path.isfile(os.path.join(self.tempdir, path)))
