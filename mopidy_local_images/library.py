from __future__ import unicode_literals

import glob
import hashlib
import imghdr
import logging
import os
import os.path
import uritools

from mopidy import local
from mopidy.audio import scan
from mopidy.exceptions import ExtensionError
from mopidy.local.translator import local_track_uri_to_file_uri
from mopidy.utils.path import get_or_create_file, uri_to_path

from . import Extension

logger = logging.getLogger(__name__)


class ImageLibrary(local.Library):

    name = 'images'

    libraries = []

    def __init__(self, config):
        ext_config = config[Extension.ext_name]
        libname = ext_config['library']
        try:
            lib = next(lib for lib in self.libraries if lib.name == libname)
            self.library = lib(config)
        except StopIteration:
            raise ExtensionError('Local library %s not found' % libname)
        logger.debug('Using %s as the local library', libname)
        try:
            self.media_dir = config['local']['media_dir']
        except KeyError:
            raise ExtensionError('Mopidy-Local not enabled')
        self.base_uri = ext_config['base_uri']
        if ext_config['image_dir']:
            self.image_dir = ext_config['image_dir']
        else:
            self.image_dir = Extension.get_or_create_data_dir(config)
        self.patterns = map(str, ext_config['album_art_files'])
        self.scanner = scan.Scanner(config['local']['scan_timeout'])

    def load(self):
        return self.library.load()

    def lookup(self, uri):
        return self.library.lookup(uri)

    def browse(self, uri):
        return self.library.browse(uri)

    def search(self, query=None, limit=100, offset=0, uris=None, exact=False):
        return self.library.search(query, limit, offset, uris, exact)

    def begin(self):
        return self.library.begin()

    def add(self, track):
        # mopidy#838: tracks without albums cannot have images
        if track.album and track.album.name:
            try:
                uri = local_track_uri_to_file_uri(track.uri, self.media_dir)
                images = self.scan(uri)
                album = track.album.copy(images=images)  # TODO: append?
                track = track.copy(album=album)
                logger.debug('Adding %r', track)
            except Exception as e:
                logger.warn('Error extracting images for %s: %s', track.uri, e)
        else:
            logger.debug('Skipping non-album track %s', track.uri)
        self.library.add(track)

    def remove(self, uri):
        self.library.remove(uri)

    def flush(self):
        return self.library.flush()

    def close(self):
        self.library.close()
        self.cleanup()

    def clear(self):
        try:
            for root, dirs, files in os.walk(self.image_dir, topdown=False):
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                for name in files:
                    os.remove(os.path.join(root, name))
        except Exception as e:
            logger.warn('Error clearing image directory: %s', e)
        return self.library.clear()

    def cleanup(self):
        logger.info('Cleaning up image directory')
        uris = set()
        for track in self.library.begin():
            if track.album and track.album.images:
                uris.update(track.album.images)
        self.library.close()

        for root, _, files in os.walk(self.image_dir):
            for name in files:
                if uritools.urijoin(self.base_uri, name) not in uris:
                    path = os.path.join(root, name)
                    logger.info('Deleting file %s', path)
                    os.remove(path)

    def scan(self, uri):
        logger.debug('Scanning %s for images', uri)
        data = self.scanner.scan(uri)
        tags = data['tags']
        images = []
        # use 'image' tag if available, smaller 'preview-image' otherwise
        for image in tags.get('image', []) or tags.get('preview-image', []):
            try:
                images.append(self.get_or_create_image_file(None, image.data))
            except Exception as e:
                logger.warn('Cannot extract images for %s: %s', uri, e)
        dirname = os.path.dirname(uri_to_path(uri))
        for pattern in self.patterns:
            for path in glob.glob(os.path.join(dirname, pattern)):
                try:
                    images.append(self.get_or_create_image(path))
                except Exception as e:
                    logger.warn('Cannot read album art from %s: %s', path, e)
        return images

    def get_or_create_image_file(self, path, data=None):
        what = imghdr.what(path, data)
        if not what:
            raise ValueError('Unknown image type')
        if not data:
            data = open(path).read()
        name = hashlib.md5(data).hexdigest() + '.' + what
        path = os.path.join(self.image_dir, name)
        get_or_create_file(str(path), True, data)
        return uritools.urijoin(self.base_uri, name)
