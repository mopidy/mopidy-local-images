from __future__ import unicode_literals

import base64
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

GIF_DATA = base64.b64decode(b"""
R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=
""")

GIF_NAME = '%s-%dx%d.%s' % (hashlib.md5(GIF_DATA).hexdigest(), 1, 1, 'gif')

PNG_DATA = base64.b64decode(b"""
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVQYV2P4DwABAQEAWk1v8QAAA
ABJRU5ErkJggg==
""")

PNG_NAME = '%s-%dx%d.%s' % (hashlib.md5(PNG_DATA).hexdigest(), 1, 1, 'png')

JPEG_DATA = base64.b64decode(b"""
/9j/4AAQSkZJRgABAQEAYABgAAD/4QAWRXhpZgAASUkqAAgAAAAAAAAAAAD/2wBDAAEBAQEBAQEB
AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/
2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
AQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAU
EAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAA
AAAAAAD/2gAMAwEAAhEDEQA/AL+AAf/Z
""")

JPEG_NAME = '%s-%dx%d.%s' % (hashlib.md5(JPEG_DATA).hexdigest(), 1, 1, 'jpeg')

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

    def test_load(self):
        self.library.load()
        mock_library.load.assert_called_with()

    def test_browse(self):
        self.library.browse(b'local:directory')
        mock_library.browse.assert_called_with(b'local:directory')

    def test_lookup(self):
        self.library.lookup(b'local:track:foo.mp3')
        mock_library.lookup.assert_called_with(b'local:track:foo.mp3')

    def test_search(self):
        self.library.search({})
        mock_library.search.assert_called_with({}, 100, 0, None, False)

    @unittest.skipUnless(hasattr(mock_library, 'get_distinct'), 'Mopidy v1.0')
    def test_get_distinct(self):
        self.library.get_distinct('album')
        mock_library.get_distinct.assert_called_with('album', None)

    @unittest.skipUnless(hasattr(mock_library, 'get_images'), 'Mopidy v1.0')
    def test_get_images(self):
        self.library.get_images([b'local:track:foo.mp3'])
        mock_library.get_images.assert_called_with([b'local:track:foo.mp3'])

    @unittest.skipUnless(hasattr(mock_library, 'get_images'), 'Mopidy v1.0')
    @mock.patch.object(mock_library, 'get_images')
    def test_get_images_size(self, mock_get_images):
        from mopidy.models import Image
        mock_get_images.return_value = {
            b'local:track:foo.mp3': [Image(uri='/images/foo-640x480.jpeg')],
            b'local:track:bar.mp3': [Image(uri='bar.png', width=10, height=20)]
        }

        images = self.library.get_images([b'local:track:foo.mp3'])
        self.assertEqual(640, images[b'local:track:foo.mp3'][0].width)
        self.assertEqual(480, images[b'local:track:foo.mp3'][0].height)
        self.assertEqual(10, images[b'local:track:bar.mp3'][0].width)
        self.assertEqual(20, images[b'local:track:bar.mp3'][0].height)

    def test_begin(self):
        self.library.begin()
        mock_library.begin.assert_called_with()

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

    def test_remove(self):
        self.library.remove(b'local:track:foo.mp3')
        mock_library.remove.assert_called_with(b'local:track:foo.mp3')

    def test_clear(self):
        self.library.clear()
        mock_library.clear.assert_called_with()

    @mock.patch.object(scan.Scanner, 'scan')
    def test_scan(self, mock_scan):
        mock_scan.return_value = {
            'tags': {
                'image': [GIF_DATA, PNG_DATA],
                'preview-image': [JPEG_DATA]
            }
        }

        album = Album(name='foo')
        track = Track(uri=b'local:track:foo.mp3', album=album)
        images = ['/images/' + name for name in GIF_NAME, PNG_NAME, JPEG_NAME]
        image_track = track.copy(album=album.copy(images=images))

        self.library.add(track)
        mock_library.add.assert_called_with(image_track, None, None)
        self.assertTrue(os.path.isfile(os.path.join(self.tempdir, GIF_NAME)))
        self.assertTrue(os.path.isfile(os.path.join(self.tempdir, PNG_NAME)))
        self.assertTrue(os.path.isfile(os.path.join(self.tempdir, JPEG_NAME)))

        self.library.close()
        self.assertEqual(os.listdir(self.tempdir), [])
