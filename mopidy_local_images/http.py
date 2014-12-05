from __future__ import unicode_literals

import logging
import os
import tornado.web

from . import Extension

logger = logging.getLogger(__name__)


class IndexHandler(tornado.web.RequestHandler):

    def initialize(self, root):
        self.root = root

    def get(self, path):
        return self.render('index.html', images=self.uris())

    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), 'www')

    def uris(self):
        for _, _, files in os.walk(self.root):
            for name in files:
                yield name  # TODO: relative path for directory hierarchy


def factory(config, core):
    # mopidy#875: handle exceptions from WebApp factory
    try:
        ext_config = config[Extension.ext_name]
        if ext_config['image_dir']:
            image_dir = ext_config['image_dir']
        else:
            image_dir = Extension.get_or_create_data_dir(config)
    except Exception as e:
        logger.error('Error starting %s: %s', Extension.dist_name, e)
        return []
    logger.info('Starting %s request handler', Extension.dist_name)
    return [
        (r'/(index.html)?', IndexHandler, {'root': image_dir}),
        (r'/(.+)', tornado.web.StaticFileHandler, {'path': image_dir})
    ]
