from __future__ import unicode_literals

import unittest

from mopidy_local_images import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()
        config = ext.get_default_config()
        self.assertIn('[local-images]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()
        schema = ext.get_config_schema()
        self.assertIn('library', schema)
        self.assertIn('base_uri', schema)
        self.assertIn('image_dir', schema)
        self.assertIn('album_art_files', schema)
