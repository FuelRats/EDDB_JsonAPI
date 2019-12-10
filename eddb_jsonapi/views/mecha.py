import json

from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text, inspect, func
from ..edsmmodels import DBSession, System

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


@view_defaults(renderer='../templates/mytemplate.jinja2')
@view_config(route_name='mecha', renderer='json')
def mecha(request):
    """
    Mecha dedicated endpoint that tries to be smrt about searching.
    :param request: The Pyramid request object
    :return: A JSON response
    """
    if 'name' not in request.params:
        return {'meta': {'error': 'No search term in \'name\' parameter!'}}
    candidates = []
    name = request.params['name']
    pmatch = DBSession.query(System).filter(System.name == name)
    if pmatch.count() > 0:
        for candidate in pmatch:
            candidates.append({'name': candidate.name, 'similarity': '1.0'})
        return {'meta': {'name': name, 'type': 'Perfect match'}, 'data': candidates}
    # Try an indexed ilike on the name, trailing wildcard only.
    sql = text(f"SELECT *, similarity(name,  '{name}') AS similarity FROM systems "
               f"WHERE name ILIKE '{name}%' ORDER BY similarity DESC LIMIT 5")
    result = DBSession.execute(sql)
    if result.returns_rows:
        for candidate in result:
            candidates.append(candidate)
    else:
        # Try a dmeta search instead.
        sql = text(f"SELECT *, similarity(name,  {name}) AS similarity FROM systems "
                   f"WHERE metaphone(name, '5') = metaphone('{name}', "
                   f"'5') ORDER BY similarity DESC LIMIT 5")
        result = DBSession.execute(sql)
        if result.count() > 0:
            for candidate in result:
                candidates.append(candidate)
        else:
            return {'meta': {'name': name, 'error': 'No hits.'}}

    return {'meta': {'name': name}, 'data': candidates}
