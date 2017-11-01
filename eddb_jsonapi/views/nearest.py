from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text

from ..mymodels import DBSession
from ..mymodels import Body
from ..mymodels import Station
import json

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
@view_config(route_name='nearest', renderer='json')
def nearest(request):
    try:
        x = request.params['x']
        y = request.params['y']
        z = request.params['z']
        if 'limit' in request.params:
            limit = request.params['limit']
        else:
            limit = 10
        if 'include' in request.params:
            include = True
        else:
            include = False
        sql = text('SELECT *,(sqrt((populated_systems.X - ' + x + ')^2 + (populated_systems.Y - ' +
                   y + ')^2 + (populated_systems.Z - ' + z + '0)^2)) as DISTANCE from '
                                                             'populated_systems ORDER BY (sqrt((populated_systems.X - ' + x + ')^2 + ' +
                   '(populated_systems.Y - ' + y + ')^2 + (populated_systems.Z - ' + z + ')^2)) '
                                                                                         ' LIMIT ' + str(limit) + ';')
        result = DBSession.execute(sql)
        candidates = []
        ids = []
        for row in result:
            candidates.append({'name': row['name'], 'distance': row['distance'], 'id': row['id']})
            ids.append(row['id'])
        if include:
            query = DBSession.query(Body).filter(Body.system_id.in_(tuple(ids)))
            results = query.all()
            bodies = []
            for row in results:
                bodies.append({'id': row.id, 'system_id': row.system_id, 'spectral_class':
                    row.spectral_class})
            query = DBSession.query(Station).filter(Station.system_id.in_(tuple(ids)))
            results = query.all()
            stations = []
            for row in results:
                stations.append({'id': row.id, 'system_id': row.system_id, 'max_landing_pad_size':
                                 row.max_landing_pad_size, 'is_planetary': row.is_planetary})
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    if results:
        return {'meta': {'query_x': x, 'query_y': y, 'query_z': z, 'limit': limit},
                'candidates': candidates, 'included': { 'bodies': bodies, 'stations': stations}}
    else:
        return {'meta': {'query_x': x, 'query_y': y, 'query_z': z, 'limit': limit},
                'candidates': candidates}