from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text, inspect
from ..mymodels import DBSession, System


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
valid_searches = {"lev", "soundex", "meta", "dmeta"}


@view_defaults(renderer='../templates/mytemplate.jinja2')
@view_config(route_name='search', renderer='json')
def search(request):
    try:
        name = request.params['name']
        if 'type' in request.params:
            searchtype = request.params['type']
            if searchtype not in valid_searches:
                return {'meta': {'error': 'Invalid search type ' + searchtype + ' specified'}}
        else:
            searchtype = 'lev'
        if 'name' not in request.params:
            return {'meta': {'error': 'No name specified.'}}
        if searchtype == 'lev':
            sql = text('SELECT *, levenshtein(name, \'' + name + '\') AS similarity FROM systems ' +
                       'WHERE name ~* \'' + name + '\' ORDER BY similarity DESC')
        if searchtype == 'soundex':
            sql = text('SELECT *, similarity(name, \'' + name +
                       '\') AS similarity FROM systems WHERE soundex(name) ' +
                       '= soundex(\'' + name + '\') ORDER BY similarity(name, \'' +
                       name + '\') DESC')
        if searchtype == 'meta':
            if 'sensitivity' not in request.params:
                sensitivity = 5
            else:
                sensitivity = request.params['sensitivity']
            sql = text('SELECT *, similarity(name, \'' + name + '\') AS similarity FROM systems ' +
                       'WHERE metaphone(name, ' + str(sensitivity) + ') = metaphone(\'' + name + '\', ' +
                       str(sensitivity) + ') ORDER BY similarity DESC')
        if searchtype == 'dmeta':
            sql = text('SELECT *, similarity(name, \'' + name + '\') AS similarity FROM systems ' +
                       'WHERE dmetaphone(name) = dmetaphone(\'' + name + '\') ORDER BY similarity DESC')
        result = DBSession.execute(sql)

        candidates = []
        ids = []
        for row in result:
            candidates.append({'name': row['name'], 'similarity': row['similarity'], 'id': row['id']})
            ids.append(row['id'])
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'meta': {'name': name, 'type': searchtype}, 'data': candidates}
