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

    add_supports_tags_and_duration = True

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

    def browse(self, uri):
        return self.library.browse(uri)

    def get_distinct(self, field, query=None):
        return self.library.get_distinct(field, query)

    def get_images(self, uris):
        return self.library.get_images(uris)

    def lookup(self, uri):
        return self.library.lookup(uri)

    def search(self, query=None, limit=100, offset=0, uris=None, exact=False):
        return self.library.search(query, limit, offset, uris, exact)

    def begin(self):
        return self.library.begin()

    def add(self, track, tags=None, duration=None):
        if track.album and track.album.name:  # require existing album
            try:
                uri = local_track_uri_to_file_uri(track.uri, self.media_dir)
                images = self._extract_images(uri, tags or self._scan(uri))
                album = track.album.copy(images=images)
                track = track.copy(album=album)
            except Exception as e:
                logger.warn('Error extracting images for %s: %s', uri, e)
        if getattr(self.library, 'add_supports_tags_and_duration', False):
            self.library.add(track, tags, duration)
        else:
            self.library.add(track)

    def remove(self, uri):
        self.library.remove(uri)

    def flush(self):
        return self.library.flush()

    def close(self):
        self.library.close()
        self._cleanup()

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

    def _cleanup(self):
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

    def _extract_images(self, uri, tags):
        path = uri_to_path(uri)
        dirname = os.path.dirname(path)
        images = set()  # filter duplicate URIs, e.g. internal/external
        for image in tags.get('image', tags.get('preview-image', [])):
            try:
                # support both gst.Buffer and plain str/bytes type
                data = getattr(image, 'data', image)
                images.add(self._get_or_create_image_file(path, data))
            except Exception as e:
                logger.warn('Error extracting images: %r', e)
        for pattern in self.patterns:
            for imgpath in glob.glob(os.path.join(dirname, pattern)):
                try:
                    images.add(self._get_or_create_image_file(imgpath))
                except Exception as e:
                    logger.warn('Cannot read image %s: %s', imgpath, e)
        return images

    def _get_or_create_image_file(self, path, data=None):
        what = imghdr.what(path, data)
        if not what:
            raise ValueError('Unknown image type')
        if not data:
            data = open(path).read()
        name = hashlib.md5(data).hexdigest() + '.' + what
        path = os.path.join(self.image_dir, name)
        get_or_create_file(str(path), True, data)
        return uritools.urijoin(self.base_uri, name)

    def _scan(self, uri):
        logger.debug('Scanning %s for images', uri)
        data = self.scanner.scan(uri)
        return data['tags']
