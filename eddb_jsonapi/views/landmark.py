from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from sqlalchemy import text, inspect
from ..edsmmodels import DBSession, Landmark
import transaction


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
@view_config(route_name='landmark', renderer='json')
def landmark(request):
    if "list" in request.params:
        sql = text("SELECT * from landmarks WHERE TRUE")
        result = DBSession.execute(sql)
        landmarks = []
        for row in result:
            landmarks.append({'name': row['name'], 'x': row['x'], 'y': row['y'],
                              'z': row['z']})
        return {'meta': {'count': len(landmarks)}, 'landmarks': landmarks}
    if "add" in request.params:
        dbsession = DBSession()
        name = str(request.params['name']).Title()
        sql = text(f"SELECT * FROM systems WHERE name ~* '{name}' LIMIT 1")
        result = dbsession.execute(sql)
        sql2 = text(f"SELECT * FROM landmarks WHERE TRUE")
        result2 = dbsession.execute(sql2)
        if name in result2:
            return {'meta': {'error': 'System is already a landmark.'}}
        if result.rowcount > 0:
            for row in result:
                x = float(row['coords']['x'])
                y = float(row['coords']['y'])
                z = float(row['coords']['z'])
            newlandmark = Landmark(name=name, x=x, y=y, z=z)
            dbsession.add(newlandmark)
            transaction.commit()
            return {'meta': {'success': 'System added as a landmark.'}}
        else:
            return {'meta': {'error': 'System not found.'}}
    try:
        name = str(request.params['name'])
        sql = text(f"SELECT * FROM systems WHERE name = '{name}' LIMIT 1")
        result = DBSession.execute(sql)
        if result.rowcount > 0:
            for row in result:
                x = float(row['coords']['x'])
                y = float(row['coords']['y'])
                z = float(row['coords']['z'])
            sql = text(f"SELECT *,(sqrt((cast(landmarks.x AS FLOAT) - {x}"
                       f")^2 + (cast(landmarks.y AS FLOAT) - {y}"
                       f")^2 + (cast(landmarks.z AS FLOAT) - {z}"
                       f")^2)) as DISTANCE from landmarks ORDER BY DISTANCE LIMIT 1;")

            result = DBSession.execute(sql)
            candidates = []
            ids = []
            for row in result:
                candidates.append({'name': row['name'], 'distance': row['distance']})
        else:
            return {'meta': {'error': 'System not found.'}}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'meta': {'name': name},
            'landmarks': candidates}
