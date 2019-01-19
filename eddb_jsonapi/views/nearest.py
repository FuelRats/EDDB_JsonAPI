from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text, inspect
from ..edsmmodels import DBSession, Body, Station


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


@view_defaults(renderer='../templates/mytemplate.jinja2')
@view_config(route_name='nearest', renderer='json')
def nearest(request):
    try:
        x = float(request.params['x'])
        y = float(request.params['y'])
        z = float(request.params['z'])
        if 'limit' in request.params:
            limit = int(request.params['limit'])
        else:
            limit = 10
        if 'include' in request.params:
            include = True
        else:
            include = False
        if 'cubesize' in request.params:
            cubesize = int(request.params['cubesize'])
        else:
            cubesize = 200
        if 'aggressive' in request.params:
            sql = text(f"SELECT *,(sqrt((cast(systems.coords->>\'x\' AS FLOAT) - {x})^2 +"
                       f"(cast(systems.coords->>\'y\' AS FLOAT) - {y}"
                       f")^2 + (cast(systems.coords->>\'z\' AS FLOAT) - {z})^2)) as DISTANCE from "
                       f"systems WHERE cast(coords->>\'x\' AS FLOAT) BETWEEN {str(float(x)-cubesize)} AND"
                       f"{str(float(x)+cubesize)} AND cast(coords->>\'y\' AS FLOAT) BETWEEN {str(float(y)-cubesize)}"
                       f" AND {str(float(y)+cubesize)} AND cast(coords->>\'z\' AS FLOAT) BETWEEN "
                       f"{str(float(z)-cubesize)} AND {str(float(z)+cubesize)}"
                       f" ORDER BY DISTANCE LIMIT {str(limit)};")
        else:
            sql = text(f"SELECT *,(sqrt((cast(populated_systems.coords->>'x' AS FLOAT) - {x}"
                       f")^2 + (cast(populated_systems.coords->>'y' AS FLOAT) - {y}"
                       f"y)^2 + (cast(populated_systems.coords->>'z' AS FLOAT) - {z}"
                       f")^2)) as DISTANCE from populated_systems ORDER BY DISTANCE LIMIT {str(limit)};")

        result = DBSession.execute(sql)
        candidates = []
        ids = []
        bodies = []
        stations = []
        for row in result:
            candidates.append({'name': row['name'], 'distance': row['distance'], 'id': row['id']})
            ids.append(row['id'])
        if include:
            query = DBSession.query(Body).filter(Body.systemId.in_(tuple(ids)))
            results = query.all()
            for row in results:
                bodies.append(object_as_dict(row))

            query = DBSession.query(Station).filter(Station.systemId.in_(tuple(ids)))
            results = query.all()
            for row in results:
                stations.append(object_as_dict(row))

    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    if bodies:
        return {'meta': {'query_x': x, 'query_y': y, 'query_z': z, 'limit': limit, 'cubesize': cubesize,
                         'included': include},
                'candidates': candidates, 'included': {'bodies': bodies, 'stations': stations}}
    else:
        return {'meta': {'query_x': x, 'query_y': y, 'query_z': z, 'limit': limit, 'cubesize':cubesize,
                         'included': include},
                'data': candidates}
