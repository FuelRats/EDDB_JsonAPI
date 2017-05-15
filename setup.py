import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'waitress',
    'sqlalchemy',
    'zope.sqlalchemy', 'requests', 'odo', 'wsgicors', 'pyramid_jsonapi',
    'psycopg2', 'odo', 'pyramid_beaker', 'aiopyramid', 'gunicorn'
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]

setup(name='EDDB_JsonAPI',
      version='0.1',
      description='EDDB_JsonAPI',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = eddb_jsonapi:main
      [console_scripts]
      initialize_EDDB_JsonAPI_db = eddb_jsonapi.initdb:main
      """,
      )
