from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext

__version__ = '1.0.0'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-Local-Images'
    ext_name = 'local-images'
    version = __version__

    def get_default_config(self):
        return config.read(os.path.join(os.path.dirname(__file__), 'ext.conf'))

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['library'] = config.String()
        schema['base_uri'] = config.String(optional=True)
        schema['image_dir'] = config.String(optional=True)
        schema['album_art_files'] = config.List(optional=True)
        return schema

    def setup(self, registry):
        from .library import ImageLibrary
        ImageLibrary.libraries = registry['local:library']
        registry.add('local:library', ImageLibrary)
        registry.add('http:app', {'name': 'images', 'factory': self.webapp})

    def webapp(self, config, core):
        from .web import ImageHandler, IndexHandler
        if config[self.ext_name]['image_dir']:
            image_dir = config[self.ext_name]['image_dir']
        else:
            image_dir = self.get_data_dir(config)
        return [
            (r'/(index.html)?', IndexHandler, {'root': image_dir}),
            (r'/(.+)', ImageHandler, {'path': image_dir})
        ]

    @classmethod
    def get_or_create_data_dir(cls, config):
        data_dir = cls().get_data_dir(config)
        migrate_old_data_dir(config, data_dir)
        return data_dir


def migrate_old_data_dir(config, new_dir):
    # Remove this method when we're confident most users have upgraded away
    # from Mopidy 1.0.
    old_dir = os.path.join(config['core']['data_dir'], b'local', b'images')
    if not os.path.isdir(old_dir):
        return
    logger.info('Migrating Mopidy-Local-Images to new data dir')
    for filename in os.listdir(old_dir):
        old_path = os.path.join(old_dir, filename)
        new_path = os.path.join(new_dir, filename)
        logger.info('Moving %r to %r', old_path, new_path)
        os.rename(old_path, new_path)
    os.rmdir(old_dir)
