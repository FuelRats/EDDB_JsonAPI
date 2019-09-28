from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response

from sqlalchemy import engine_from_config
from . import edsmmodels
import pyramid_jsonapi
from pyramid_beaker import set_cache_regions_from_settings
from pyramid_beaker import session_factory_from_settings


def request_factory(environ):
    request = Request(environ)
    if request.is_xhr:
        request.response = Response()
        request.response.headerlist = []
        request.response.headerlist.extend(
            (
                ('Access-Control-Allow-Origin', '*'),
                ('Content-Type', 'application/json')
            )
        )
    return request


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    session_factory = session_factory_from_settings(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    edsmmodels.DBSession.configure(bind=engine)
    #edsmmodels.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.set_session_factory(session_factory)
    config.include('pyramid_beaker')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('nearest', '/nearest')
    config.add_route('search', '/search')
    config.set_request_factory(request_factory)
    pj = pyramid_jsonapi.PyramidJSONAPI(config, edsmmodels, lambda view: edsmmodels.DBSession)
    pj.create_jsonapi_using_magic_and_pixie_dust()

    config.scan()

    return config.make_wsgi_app()
