from pyramid.view import (
    view_config
)

from .. import __version__


@view_config(route_name='version', renderer="json")
def version(request):
    return {
        'data': {
            'type': 'version',
            'id': 1,
            'attributes': {
                'version': __version__
            }
        }
    }
