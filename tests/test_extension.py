from __future__ import unicode_literals

from mopidy_local_images import Extension


def test_get_default_config():
    ext = Extension()
    config = ext.get_default_config()
    assert '[local-images]' in config
    assert 'enabled = true' in config


def test_get_config_schema():
    ext = Extension()
    schema = ext.get_config_schema()
    assert 'library' in schema
    assert 'base_uri' in schema
    assert 'image_dir' in schema
    assert 'album_art_files' in schema
