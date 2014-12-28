from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext

__version__ = '0.1.2'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-Local-Images'
    ext_name = 'local-images'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['library'] = config.String()
        schema['base_uri'] = config.String(optional=True)
        schema['image_dir'] = config.String(optional=True)
        schema['album_art_files'] = config.List(optional=True)
        return schema

    def setup(self, registry):
        from .library import ImageLibrary
        from .http import factory

        ImageLibrary.libraries = registry['local:library']

        registry.add('local:library', ImageLibrary)
        registry.add('http:app', {'name': 'images', 'factory': factory})

    @classmethod
    def get_or_create_data_dir(cls, config):
        try:
            data_dir = config['local']['data_dir']
        except KeyError:
            from mopidy.exceptions import ExtensionError
            raise ExtensionError('Mopidy-Local not enabled')
        # FIXME: mopidy.utils.path is undocumented
        from mopidy.utils.path import get_or_create_dir
        return get_or_create_dir(os.path.join(data_dir, b'images'))
