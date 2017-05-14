EDDB_JsonAPI README
==================

This is meant to live behind a nginx proxy with SSL.
You must switch backends to Postgres to run initdb.py. If you MUST use another backend,
you will have to modify initdb.py to work with your chosen backend.

You should use python3.5 or newer as your virtualenv base.

Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/pip install -e .

- Copy development.ini or production.ini to eddb_jsonapi.ini and configure.
  If you want to serve SSL directly from the application, you must use gunicorn
  instead of waitress.

- Ensure you have Postgres >9.3, with pg_trgm installed and a user created for the API.
  The user must be a Postgres Superuser to be able to perform COPY operations from the
  EDDB dumps.

- $VENV/bin/python initdb.py eddb_jsonapi#mainapp

- $VENV/bin/pserve eddb_jsonapi.ini
