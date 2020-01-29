import json

from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
import pyramid.httpexceptions as hex
from sqlalchemy import text, inspect, func
from ..edsmmodels import DBSession, System, Permits

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
    permsystems = DBSession.query(Permits)
    perm_systems = []
    for system in permsystems:
        perm_systems.append(system.id64)
    name = request.params['name']
    if len(name) < 3:
        return {'meta': {'error': 'Search term too short (Min 3 characters)'}}
    pmatch = DBSession.query(System).filter(System.name == name)
    for candidate in pmatch:
        if candidate.id64 in perm_systems:
            candidates.append({'name': candidate.name, 'similarity': 1, 'permit_required': True})
        else:
            candidates.append({'name': candidate.name, 'similarity': 1, 'permit_required': False})
    if len(candidates) > 0:
        return {'meta': {'name': name, 'type': 'Perfect match'}, 'data': candidates}
    # Try an indexed ilike on the name, no wildcard.
    result = DBSession.query(System, func.similarity(System.name, name).label('similarity')).\
        filter(System.name.ilike(name)).order_by(func.similarity(System.name, name).desc())
    for candidate in result:
        if candidate[0].id64 in perm_systems:
            candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': True})
        else:
            candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': False})
    if len(candidates) < 1:
        # Try an ILIKE with a wildcard at the end.
        pmatch = DBSession.query(System, func.similarity(System.name, name).label('similarity')).\
            filter(System.name.ilike(name+"%")).order_by(func.similarity(System.name, name).desc())
        for candidate in pmatch:
            if candidate.id64 in perm_systems:
                candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': True})
            else:
                candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': False})
        if len(candidates) > 0:
            return {'meta': {'name': name, 'type': 'wildcard'}, 'data': candidates}
        # Try a trigram similarity search if English-ish system name
        if len(name.split(' ')) < 2:
            pmatch = DBSession.query(System, func.similarity(System.name, name).label('similarity')).\
                filter(System.name % name).order_by(func.similarity(System.name, name).desc())
            if pmatch.count() > 0:
                for candidate in pmatch:
                    # candidates.append({'name': candidate[0].name, 'similarity': "1.0"}
                    if candidate[0].id64 in perm_systems:
                        candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': True})
                    else:
                        candidates.append({'name': candidate[0].name, 'similarity': candidate[1], 'permit_required': False})

        else:
            # Last effort, try a dimetaphone search.

            sql = text(f"SELECT *, similarity(name, '{name}') AS similarity FROM systems "
                       f"WHERE dmetaphone(name) = dmetaphone('{name}') ORDER BY similarity DESC LIMIT 5")
            result = DBSession.execute(sql)
            for candidate in result:
                if candidate.id64 in perm_systems:
                    candidates.append({'name': candidate.name, 'similarity': candidate.similarity, 'permit_required': True})
                else:
                    candidates.append({'name': candidate.name, 'similarity': candidate.similarity, 'permit_required': False})
    if len(candidates) < 1:
        # We ain't got shit. Give up.
        return {'meta': {'name': name, 'error': 'No hits.'}}
    return {'meta': {'name': name}, 'data': candidates}
