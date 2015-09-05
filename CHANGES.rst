v1.0.0 (2015-09-05)
-------------------

- Require Mopidy v1.1 or later.

- Use ``Extension.get_data_dir()`` as default image directory.


v0.3.3 (2015-06-17)
-------------------

- Remove `.coveragerc`.


v0.3.2 (2015-06-17)
-------------------

- Update ``local.translator`` imports for Mopidy v1.1.

- Update build/test environment.


v0.3.1 (2015-03-20)
-------------------

- Fix width/height for JPEG images.


v0.3.0 (2015-03-20)
-------------------

- Extract image dimensions.

- Support aggressive browser caching.


v0.2.0 (2015-03-15)
-------------------

- Support local library methods added with Mopidy v0.20.

- Avoid scanning each track twice by using the tags passed to
  ``Library.add`` with Mopidy v0.20.


v0.1.3 (2015-02-03)
-------------------

- Remove link to `mopidy.css`.

- Fix error when scanning external album art.


v0.1.2 (2014-12-28)
-------------------

- Use `preview-image` tag if `image` tag is not available.


v0.1.1 (2014-12-06)
-------------------

- Fix ``Library.search`` delegation.


v0.1.0 (2014-12-05)
-------------------

- Initial release, based on Mopidy-Local-SQLite.
