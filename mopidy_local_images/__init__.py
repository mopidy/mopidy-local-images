from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext
from mopidy.exceptions import ExtensionError

__version__ = '0.3.3'

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

    @classmethod
    def get_or_create_data_dir(cls, config):
        try:
            data_dir = config['local']['data_dir']
        except KeyError:
            raise ExtensionError('Mopidy-Local not enabled')
        path = os.path.join(data_dir, b'images')
        if not os.path.isdir(path):
            logger.info('Creating directory %s', path)
            os.makedirs(path, 0o755)
        return path

    def webapp(self, config, core):
        from .web import ImageHandler, IndexHandler
        if config[self.ext_name]['image_dir']:
            image_dir = config[self.ext_name]['image_dir']
        else:
            image_dir = self.get_or_create_data_dir(config)
        return [
            (r'/(index.html)?', IndexHandler, {'root': image_dir}),
            (r'/(.+)', ImageHandler, {'path': image_dir})
        ]
