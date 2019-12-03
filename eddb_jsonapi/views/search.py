import json

from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text, inspect
from ..edsmmodels import DBSession, System


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_tutorial_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
valid_searches = {"lev", "soundex", "meta", "dmeta", "fulltext"}


@view_defaults(renderer='../templates/mytemplate.jinja2')
@view_config(route_name='search', renderer='json')
def search(request):
    try:
        if 'type' in request.params:
            searchtype = request.params['type']
            if searchtype not in valid_searches:
                return {'meta': {'error': 'Invalid search type ' + searchtype + ' specified'}}
        else:
            if len(request.params['name'].split()) <= 2:
                # Single or double word system name, use dmeta.
                searchtype = 'dmeta'
            else:
                # New implementation for lev, try tgrm similarity instead.
                searchtype = 'lev'
        if 'term' in request.params:
            xhr = True
            name = request.params['term'].title()
            searchtype = "lev"
        else:
            xhr = False
            name = request.params['name'].title()
        if 'limit' not in request.params:
            limit = 20
        else:
            limit = request.params['limit']
        if searchtype == 'lev':
            sql = text(f"SELECT *, similarity(name,  '{name}') AS similarity FROM systems "
                       f"WHERE name % '{name}' ORDER BY similarity DESC LIMIT {limit}")
        if searchtype == 'soundex':
            sql = text(f"SELECT *, similarity(name, '{name}') AS similarity FROM systems "
                       f"WHERE soundex(name) = soundex('{name}') ORDER BY "
                       f"similarity(name, '{name}') DESC LIMIT {limit}")
        if searchtype == 'meta':
            if 'sensitivity' not in request.params:
                sensitivity = 5
            else:
                sensitivity = request.params['sensitivity']
            sql = text(f"SELECT *, similarity(name,  {name}) AS similarity FROM systems "
                       f"WHERE metaphone(name, '{str(sensitivity)}') = metaphone('{name}', "
                       f"'{str(sensitivity)}') ORDER BY similarity DESC LIMIT {str(limit)}")
        if searchtype == 'dmeta':
            sql = text(f"SELECT *, similarity(name, '{name}') AS similarity FROM systems "
                       f"WHERE dmetaphone(name) = dmetaphone('{name}') ORDER BY similarity DESC LIMIT {str(limit)}")
        if searchtype == "fulltext":
            sql = text(f"SELECT name FROM systems WHERE name LIKE '{name}%' DESC LIMIT {str(limit)}")
        candidates = []
        ids = []

        # Check if some clever idjit is searching for an exact system match.
        idjitresult = DBSession.query(System).filter(System.name == name)
        if idjitresult.count() > 0:
            for candidate in idjitresult:
                candidates.append({'name': candidate.name, 'similarity': 'Perfect match'})
            return {'meta': {'name': name, 'type': 'Perfect match'}, 'data': candidates}
        # Carry on.
        result = DBSession.execute(sql)

        if xhr is True:
            for row in result:
                candidates.append(row['name'])
            response = Response(content_type='application/json')
            response.text = json.dumps(candidates)
            return response
        else:
            for row in result:
                candidates.append({'name': row['name'], 'similarity': row['similarity'], 'id': row['id']})
                ids.append(row['id'])
            return {'meta': {'name': name, 'type': searchtype, 'limit': limit}, 'data': candidates}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

