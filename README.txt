EDDB_JsonAPI README
==================

This is meant to live behind a nginx proxy with SSL.
You must switch backends to Postgres to run initdb.py. If you MUST use another backend,
you will have to modify initdb.py to work with your chosen backend.

REQUIREMENTS
============

- Postgres 9.5 or newer with pg_trgm installed
- Python3.5 or newer
- Virtualenv strongly suggested
- As of May 2017, about 10-15GB of disk space in Postgres' data directories,
  and 10GB of diskspace in the APIs working directory for temporary files.
  Diskspace needed will increase with the size of EDDB's known systems.


Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/pip install -e .

- Copy development.ini or production.ini to eddb_jsonapi.ini and configure.
  If you want to serve SSL directly from the application, you must use gunicorn
  instead of waitress.

- Ensure you have Postgres >9.5, with pg_trgm installed and a user created for the API.
  The user must be a Postgres Superuser to be able to perform COPY operations from the
  EDDB dumps.

- $VENV/bin/python initdb.py eddb_jsonapi#mainapp

- $VENV/bin/pserve eddb_jsonapi.ini


Querying the API
----------------

Valid endpoints are:
/systems
/bodies
/stations
/populated_systems
/factions
/listings

JSONAPI is provided using Pyramid-JSONAPI, which is documented here:
https://colinhiggs.github.io/pyramid-jsonapi/#consuming-the-api-from-the-client-end

Filtering is done using filter[<attribute>:<operator>]=value.
Valid filters are:
* eq
* ne
* startswith
* endswith
* contains
* lt
* gt
* le
* ge
* like or ilike

All system names in systems are UPPERCASED for faster searches. Use LIKE and uppercase
your search argument for the best results. On most queries, the API should respond in
less than 200ms.

Caching is done using beaker, and keeps response times down for similar queries within
a fairly short timeframe (in case you are using a third party application which would send
the same query from several points simultaneously).
