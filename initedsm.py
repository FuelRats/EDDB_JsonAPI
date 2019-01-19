import os, sys, transaction, subprocess
from datetime import time, datetime, timedelta
#from psycopg2 import IntegrityError
from sqlalchemy.exc import IntegrityError
from odo import odo, dshape, chunks

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
    Star,
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
    settings = get_appsettings(config_uri, name='mainapp')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.execution_options = dict(stream_results=True)

    #
    # Systems
    #
    #if os.path.isfile('systemsWithCoordinates.json'):
    #    if datetime.fromtimestamp(os.path.getmtime('systemsWithCoordinates.json')) > datetime.today() - timedelta(days=7):
    #        print("Using cached systemsWithCoordinates.json")
    #else:
    #    print("Downloading systemsWithCoordinates.json from EDSM.net...")
    #    r = requests.get("https://www.edsm.net/dump/systemsWithCoordinates.json", stream=True)
    #    with open('systemsWithCoordinates.json', 'wb') as f:
    #        for chunk in r.iter_content(chunk_size=4096):
    #            if chunk:
    #                f.write(chunk)
    #    print("Downloading systems without coordinates...")
    #    r = requests.get("https://www.edsm.net/dump/systemsWithoutCoordinates.json")
    #    with open('systemsWithoutCoordinates.json', 'wb') as f:
    #        for chunk in r.iter_content(chunk_size=4096):
    #            if chunk:
    #                f.write(chunk)
    #
    #    print("Saved systems. Converting JSON to SQL.")

    ds = dshape("var *{  id: ?int64,  id64: ?int64,  name: ?string,  coords: ?json, "
                "controllingFaction: ?string,  stations: ?json,  bodies: ?json,  "
                "date: ?datetime}")
    url = str(engine.url) + "::" + System.__tablename__

    try:
        with os.scandir('.') as filelist:
            for file in filelist:
                if file.name.startswith('systemsWithCoordinates') and file.is_file():
                    t = odo(file.name, url, dshape=ds)
    except IntegrityError as e:
        print("Integrity Error during system insert: "+e)
    print("Adding systems without coordinates...")
    ds = dshape("var *{ id: ?int64, id64: ?int64, name: ?string, coords: ?json, date: ?datetime}")
    t = odo('systemsWithoutCoordinates.json', url, dshape=ds)
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
    #if os.path.isfile('systemsPopulated.json'):
    #    if datetime.fromtimestamp(os.path.getmtime('systemsPopulated.json')) > datetime.today() - timedelta(days=7):
    #        print("Using cached systemsPopulated.json")
    #else:
    #    print("Downloading systemsPopulated.json from EDSM.net...")
    #    r = requests.get("https://www.edsm.net/dump/systemsPopulated.json", stream=True)
    #    with open('systemsPopulated.json', 'wb') as f:
    #        for chunk in r.iter_content(chunk_size=4096):
    #            if chunk:
    #                f.write(chunk)
    #    print("Saved systemsPopulated.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + PopulatedSystem.__tablename__
    ds = dshape("var *{  id: ?int64,  id64: ?int64,  name: ?string,  coords: ?json,  "
                "controllingFaction: ?json,  stations: ?json,  bodies: ?json,  "
                "date: ?datetime}")
    t = odo('systemsPopulated.json', url, dshape=ds)

    print("Uppercasing system names...")
    DBSession.execute("UPDATE populated_systems SET name = UPPER(name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Creating name indexes...")
    DBSession.execute("CREATE INDEX idx_populated_system_names_trigram ON populated_systems "
                      "USING GIN(name gin_trgm_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_systems_meta_name on systems (dmetaphone(name))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_systems_sndx_name on systems (soundex(name))")
    mark_changed(DBSession())
    transaction.commit()
    print("Indexing coordinates...")
    DBSession.execute("CREATE INDEX idx_populated_system_names_btree ON populated_systems (name)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_systems_coord_x on systems (CAST(coords->>'x' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_systems_coord_y on systems (CAST(coords->>'y' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_systems_coord_z on systems (CAST(coords->>'z' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_populated_systems_coord_x on populated_systems (CAST(coords->>'x' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_populated_systems_coord_y on populated_systems (CAST(coords->>'y' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX idx_populated_systems_coord_z on populated_systems (CAST(coords->>'z' AS FLOAT))")
    mark_changed(DBSession())
    transaction.commit()

    print("Done!")

    #
    # Bodies
    #
    #if os.path.isfile('bodies.json'):
    #    if datetime.fromtimestamp(os.path.getmtime('bodies.json')) > datetime.today() - timedelta(days=7):
    #        print("Using cached bodies.json")
    #else:
    #    print("Downloading bodies.json from EDSM.net...")
    #    r = requests.get("https://www.edsm.net/dump/bodies.json", stream=True)
    #    with open('bodies.json', 'wb') as f:
    #        for chunk in r.iter_content(chunk_size=4096):
    #            if chunk:
    #                f.write(chunk)
    #print("Saved bodies.json. Converting JSON to SQL.")
    # Call shell and split files into chunks.
    #subprocess.call(["split", "-d -a 3 -C 1G --additional-suffix=.json bodies.json chunkedbodies"])
    print("Inserting planetary bodies...")
    ds = dshape("var *{  id: ?int64,  id64: ?int64,  bodyId: ?int64,  name: ?string,  "
                "discovery: ?json,  type: ?string,  subType: ?string,  offset: ?int64,  "
                "parents: ?json,  distanceToArrival: ?float64, isLandable: ?bool, "
                "gravity: ?float64, earthMasses: ?float64, radius: ?float64, surfaceTemperature: ?float64, "
                "surfacePressure: ?float64, volcanismType: ?string, atmosphereType: ?string, "
                "atmosphereComposition: ?json, terraformingState: ?string, orbitalPeriod: ?float64, "
                "semiMajorAxis: ?float64, orbitalEccentricity: ?float64, orbitalInclination: ?float64, "
                "argOfPeriapsis: ?float64, rotationalPeriod: ?float64, rotationalPeriodTidallyLocked: ?bool, "
                "axialTilt: ?float64, rings: ?json, updateTime: ?datetime, systemId: ?int64, "
                "systemId64: ?int64, systemName: ?string}")
    url = str(engine.url) + "::" + Star.__tablename__
    with os.scandir('.') as filelist:
        for file in filelist:
            if file.name.startswith('bodies') and file.is_file():
                t = odo(file.name, url, dshape=ds)
    print("Inserting stars...")
    ds = dshape("var *{ id: ?int64,  id64: ?int64,  bodyId: ?int64,  name: ?string,  "
                "discovery: ?json,  type: ?string,  subType: ?string,  offset: ?int64,  "
                "parents: ?json,  distanceToArrival: ?float64, isMainStar: ?bool, "
                "isScoopable: ?bool, age: ?int64, luminosity: ?string, absoluteMagnitude: ?float64, "
                "solarMasses: ?float64, solarRadius: ?float64, "
                "volcanismType: ?string, atmosphereType: ?string, "
                "terraformingState: ?string, orbitalPeriod: ?float64, "
                "semiMajorAxis: ?float64, orbitalEccentricity: ?float64, orbitalInclination: ?float64, "
                "argOfPeriapsis: ?float64, rotationalPeriod: ?float64, rotationalPeriodTidallyLocked: ?bool, "
                "axialTilt: ?float64, belts: ?json, updateTime: ?datetime, systemId: ?int64, systemId64: ?int64, "
                "systemName: ?string}")
    url = str(engine.url) + "::" + Body.__tablename__
    with os.scandir('.') as filelist:
        for file in filelist:
            if file.name.startswith('stars') and file.is_file():
                t = odo(file.name, url, dshape=ds)

    print("Creating indexes...")
    DBSession.execute("CREATE INDEX bodies_idx ON bodies(name text_pattern_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX systemid_idx ON bodies(\"systemId\")")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX stars_idx ON stars(name text_pattern_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX stars_systemid_idx ON stars(\"systemId\")")
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
                "distanceToArrival: ?float64, allegiance: ?string, government: ?string, "
                "economy: ?string, haveMarket: ?bool, haveShipyard: ?bool, haveOutfitting: ?bool, "
                "otherServices: ?json, updateTime: ?json, systemId: ?int64, systemId64: ?int64, "
                "systemName: ?string}")
    t = odo('stations.json', url, dshape=ds)

    print("Creating indexes...")
    DBSession.execute("CREATE INDEX index_stations_systemid_btree ON stations(\"systemId\")")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX index_stations_btree ON stations(id)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")


main()
