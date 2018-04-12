import os, sys, transaction
from datetime import time, datetime, timedelta

from odo import odo, dshape

import requests
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config
from zope.sqlalchemy import mark_changed

from eddb_jsonapi.edsmmodels import (
    DBSession,
    System,
    Body,
    Base,
    PopulatedSystem,
    Station)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini.default")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    #
    # Systems
    #
    if os.path.isfile('systemsWithCoordinates.json'):
        if datetime.fromtimestamp(os.path.getmtime('systemsWithCoordinates.json')) > datetime.today() - timedelta(days=7):
            print("Using cached systemsWithCoordinates.json")
    else:
        print("Downloading systemsWithCoordinates.json from EDSM.net...")
        r = requests.get("https://www.edsm.net/dump/systemsWithCoordinates.json", stream=True)
        with open('systemsWithCoordinates.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved systems. Converting JSON to SQL.")

    ds = dshape("var *{  id: ?int64,  id64: ?int64,  name: ?string,  coords: ?json, "
                "controllingFaction: ?string,  stations: ?json,  bodies: ?json,  "
                "date: ?datetime}")
    url = str(engine.url) + "::" + System.__tablename__
    t = odo('systemsWithCoordinates.json', url, dshape=ds)
    # Reapplying uppercase to systems, as the index being uppercased slows down searches again.
    print("Uppercasing system names...")
    DBSession.execute("UPDATE systems SET name = UPPER(name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Creating indexes...")
    DBSession.execute("CREATE INDEX index_system_names_trigram ON systems USING GIN(name gin_trgm_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX index_system_names_btree ON systems (name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")

    #
    # Populated Systems
    #
    if os.path.isfile('systemsPopulated.json'):
        if datetime.fromtimestamp(os.path.getmtime('systemsPopulated.json')) > datetime.today() - timedelta(days=7):
            print("Using cached systemsPopulated.json")
    else:
        print("Downloading systemsPopulated.json from EDSM.net...")
        r = requests.get("https://www.edsm.net/dump/systemsPopulated.json", stream=True)
        with open('systemsPopulated.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved systemsPopulated.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + PopulatedSystem.__tablename__
    ds = dshape("var *{  id: ?int64,  id64: ?int64,  name: ?string,  coords: ?json,  "
                "controllingFaction: ?string,  stations: ?json,  bodies: ?json,  "
                "date: ?datetime}")
    t = odo('jsonlines://systemsPopulated.json', url, dshape=ds)

    print("Uppercasing system names...")
    DBSession.execute("UPDATE populated_systems SET name = UPPER(name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Creating indexes...")
    DBSession.execute("CREATE INDEX index_populated_system_names_trigram ON populated_systems "
                      "USING GIN(name gin_trgm_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX index_populated_system_names_btree ON populated_systems (name)")
    mark_changed(DBSession())
    transaction.commit()

    print("Done!")

    #
    # Bodies
    #
    if os.path.isfile('bodies.json'):
        if datetime.fromtimestamp(os.path.getmtime('bodies.json')) > datetime.today() - timedelta(days=7):
            print("Using cached bodies.json")
    else:
        print("Downloading bodies.json from EDSM.net...")
        r = requests.get("https://www.edsm.net/dump/bodies.json", stream=True)
        with open('bodies.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
    print("Saved bodies.jsonl. Converting JSONL to SQL.")
    ds = dshape("var *{ id: ?int64, id64: ?int64, bodyId: ?int, name: ?string, "
                "discovery: ?json, type: ?string, subType: ?string, offset: ?int, "
                "parents: ?json, distanceToArrival: ?float, isLandable: ?bool, "
                "gravity: ?float, earthMasses: ?float, radius: ?float, surfaceTemperature: ?float, "
                "surfacePressure: ?float, volcanismType: ?string, atmosphereType: ?string, "
                "atmosphereComposition: ?json, terraformingState: ?string, orbitalPeriod: ?float, "
                "semiMajorAxis: ?float, orbitalEccentricity: ?float, orbitalInclination: ?float, "
                "argOfPeriapsis: ?float, rotationalPeriod: ?float, rotationalPeriodTidallyLocked: ?bool, "
                "axialTilt: ?float, rings: ?json, updateTime: ?datetime, systemId: ?int64, "
                "systemId64: ?int64, systemName: ?string}")
    url = str(engine.url) + "::" + Body.__tablename__
    t = odo('jsonlines://bodies.json', url, dshape=ds)
    print("Creating indexes...")
    DBSession.execute("CREATE INDEX bodies_idx ON bodies(name text_pattern_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX systemid_idx ON bodies(system_id)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")

    #
    # Stations
    #

    if os.path.isfile('stations.json'):
        if datetime.fromtimestamp(os.path.getmtime('stations.json')) > datetime.today() - timedelta(days=7):
            print("Using cached stations.json")
    else:
        print("Downloading stations.json from EDSM.net...")
        r = requests.get("https://www.edsm.net/dump/stations.json", stream=True)
        with open('stations.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved stations.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + Station.__tablename__
    ds = dshape("var *{  id: ?int64,  marketId: ?int64, type: ?string, name: ?string, "
                "distanceToArrival: ?float, allegiance: ?string, government: ?string, "
                "economy: ?string, haveMarket: ?bool, haveShipyard: ?bool, haveOutfitting: ?bool, "
                "otherServices: ?json, updateTime: ?json, systemId: ?int64, systemId64: ?int64, "
                "systemName: ?string}")
    t = odo('jsonlines://stations.json', url, dshape=ds)

    print("Creating indexes...")
    DBSession.execute("CREATE INDEX index_stations_systemid_btree ON stations(system_id)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX index_stations_btree ON stations(id)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")


main()
