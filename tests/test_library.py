from __future__ import unicode_literals

import shutil
import tempfile
import unittest

import mock

from mopidy import local
from mopidy.models import Track
from mopidy_local_images import library

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
                'base_uri': None,
                'image_dir': self.tempdir,
                'album_art_files': []
            }
        })

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_add_no_album(self):
        track = Track(name='Foo', uri='local:track:foo')
        self.library.add(track)
        mock_library.add.assert_called_with(track)

    def test_load(self):
        self.library.load()
        mock_library.load.assert_called_with()

    def test_browse(self):
        self.library.browse('uri')
        mock_library.browse.assert_called_with('uri')

    def test_get_distinct(self):
        self.library.get_distinct('field')
        mock_library.get_distinct.assert_called_with('field', None)

    def test_get_images(self):
        self.library.get_images(['uri'])
        mock_library.get_images.assert_called_with(['uri'])
        pass

    def test_lookup(self):
        self.library.lookup('uri')
        mock_library.lookup.assert_called_with('uri')

    def test_search(self):
        self.library.search({})
        mock_library.search.assert_called_with({}, 100, 0, None, False)
