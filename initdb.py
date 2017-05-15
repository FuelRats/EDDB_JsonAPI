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

from eddb_jsonapi.mymodels import (
    DBSession,
    System,
    Body,
    Base,
    PopulatedSystem,
    Faction,
    Station,
    Listing)


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
    if os.path.isfile('systems.csv'):
        if datetime.fromtimestamp(os.path.getmtime('systems.csv')) > datetime.today()-timedelta(days=7):
            print("Using cached systems.csv")
    else:
        print("Downloading systems.csv from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/systems.csv", stream=True)
        with open('systems.csv', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved systems.csv. Converting CSV to SQL.")

    ds = dshape("var *{  id: ?int64,  edsm_id: ?int64,  name: ?string,  x: ?float64,  y: ?float64,  "
                "z: ?float64,  population: ?int64,  is_populated: ?bool,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string,  security_id: ?float64,  security: ?string,  "
                "primary_economy_id: ?float64,  primary_economy: ?string,  power: ?string,  "
                "power_state: ?string,  power_state_id: ?string,  needs_permit: ?bool,  "
                "updated_at: ?int64,  simbad_ref: ?string,  controlling_minor_faction_id: ?string,  "
                "controlling_minor_faction: ?string,  reserve_type_id: ?float64,  reserve_type: ?string  }")
    url = str(engine.url) + "::" + System.__tablename__
    t = odo('systems.csv', url, dshape=ds)

    print("Uppercasing system names...")
    DBSession.execute("UPDATE systems set name = UPPER(name)")
    mark_changed(DBSession())
    transaction.commit()

    print("Creating indexes...")
    DBSession.execute("create index index_system_names_trigram on systems using gin(name gin_trgm_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("create index index_system_names_btree on systems (name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")


    #
    # Factions
    #
    if os.path.isfile('factions.json'):
        if datetime.fromtimestamp(os.path.getmtime('factions.json')) > datetime.today()-timedelta(days=7):
            print("Using cached factions.json")
    else:
        print("Downloading factions.jsonl from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/factions.jsonl", stream=True)
        with open('factions.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved factions.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + Faction.__tablename__
    ds = dshape("var *{  id: ?int64,  name: ?string,  updated_at: ?int64,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string, home_system_id: ?int64,  "
                "is_player_faction: ?bool }")
    t = odo('jsonlines://factions.json', url, dshape=ds)
    print("Done!")
    DBSession.execute("create index factions_idx on factions(id)")
    mark_changed(DBSession())
    transaction.commit()

    #
    # Populated Systems
    #
    if os.path.isfile('systems_populated.json'):
        if datetime.fromtimestamp(os.path.getmtime('systems_populated.json')) > datetime.today()-timedelta(days=7):
            print("Using cached systems.csv")
    else:
        print("Downloading systems_populated.jsonl from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/systems_populated.jsonl", stream=True)
        with open('systems_populated.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved systems_populated.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + PopulatedSystem.__tablename__
    ds = dshape("var *{  id: ?int64,  edsm_id: ?int64,  name: ?string,  x: ?float64,  y: ?float64,  "
                "z: ?float64,  population: ?int64,  is_populated: ?bool,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string,  security_id: ?float64,  security: ?string,  "
                "primary_economy_id: ?float64,  primary_economy: ?string,  power: ?string,  "
                "power_state: ?string,  power_state_id: ?string,  needs_permit: ?int64,  "
                "updated_at: ?int64,  simbad_ref: ?string,  controlling_minor_faction_id: ?string,  "
                "controlling_minor_faction: ?string,  reserve_type_id: ?float64,  reserve_type: ?string,"
                "minor_faction_presences: ?json }")
    t = odo('jsonlines://systems_populated.json', url, dshape=ds)

    print("Uppercasing system names...")
    DBSession.execute("UPDATE populated_systems set name = UPPER(name)")
    mark_changed(DBSession())
    transaction.commit()
    print("Creating indexes...")
    DBSession.execute("CREATE index index_populated_system_names_trigram on populated_systems "
                      "using gin(name gin_trgm_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE index index_populated_system_names_btree on systems (name)")
    mark_changed(DBSession())
    transaction.commit()

    print("Done!")

    #
    # Bodies
    #
    if os.path.isfile('bodies.json'):
        if datetime.fromtimestamp(os.path.getmtime('bodies.json')) > datetime.today()-timedelta(days=7):
            print("Using cached bodies.json")
    else:
        print("Downloading bodies.jsonl from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/bodies.jsonl", stream=True)
        with open('bodies.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
    print("Saved bodies.jsonl. Converting JSONL to SQL.")
    ds = dshape("var *{ id: ?int64, created_at: ?int64, updated_at: ?int64, name: ?string, "
                "system_id: ?int64, group_id: ?int64, group_name: ?string, type_id: ?int64, "
                "type_name: ?string, distance_to_arrival: ?int64, full_spectral_class: ?string, "
                "spectral_class: ?string, spectral_sub_class: ?string, luminosity_class: ?string, "
                "luminosity_sub_class: ?string, surface_temperature: ?int64, is_main_star: ?bool, "
                "age: ?int64, solar_masses: ?float64, solar_radius: ?float64, catalogue_gliese_id : ?string, "
                "catalogue_hipp_id: ?string, catalogue_hd_id: ?string, volcanism_type_id: ?int64, "
                "volcanism_type_name: ?string, atmosphere_type_id: ?int64, atmosphere_type_name: ?string, "
                "terraforming_state_id: ?int64, terraforming_state_name: ?string, earth_masses: ?float64, "
                "radius: ?int64, gravity: ?float64, surface_pressure: ?int64, orbital_period: ?float64, "
                "semi_major_axis: ?float64, orbital_eccentricity: ?float64, orbital_inclination: ?float64, "
                "arg_of_periapsis: ?float64, rotational_period: ?float64, "
                "is_rotational_period_tidally_locked: ?bool, axis_tilt: ?float64, eg_id: ?int64, "
                "belt_moon_masses: ?float64, ring_type_id: ?int64, ring_type_name: ?string, "
                "ring_mass: ?int64, ring_inner_radius: ?float64, ring_outer_radius: ?float64, "
                "rings: ?json, atmosphere_composition: ?json, solid_composition: ?json, "
                "materials: ?json, is_landable: ?bool}")
    url = str(engine.url) + "::" + Body.__tablename__
    t = odo('jsonlines://bodies.json', url, dshape=ds)
    print("Creating indexes...")
    DBSession.execute("CREATE INDEX bodies_idx on bodies(name text_pattern_ops)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE INDEX systemid_idx on bodies(system_id)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")

    #
    # Stations
    #

    if os.path.isfile('stations.json'):
        if datetime.fromtimestamp(os.path.getmtime('stations.json')) > datetime.today()-timedelta(days=7):
            print("Using cached stations.json")
    else:
        print("Downloading stations.jsonl from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/stations.jsonl", stream=True)
        with open('stations.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved stations.json. Converting JSONL to SQL.")

    url = str(engine.url) + "::" + Station.__tablename__
    ds = dshape("var *{  id: ?int64,  name: ?string,  system_id: ?int64,  updated_at: ?int64,  "
                "max_landing_pad_size: ?string,  distance_to_star: ?int64,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string,  type_id: ?int64,  type: ?string,  "
                "has_blackmarket: ?bool,  has_market: ?bool,  has_refuel: ?bool,  "
                "has_repair: ?bool,  has_rearm: ?bool,  has_outfitting: ?bool,  "
                "has_shipyard: ?bool,  has_docking: ?bool,  has_commodities: ?bool,  "
                "import_commodities: ?json,  export_commodities: ?json,  prohibited_commodities: ?json, "
                "economies: ?json, shipyard_updated_at: ?int64, outfitting_updated_at: ?int64, "
                "market_updated_at: ?int64, is_planetary: ?bool, selling_ships: ?json, "
                "selling_modules: ?json, settlement_size_id: ?text, settlement_size: ?int64, "
                "settlement_security_id: ?int64, settlement_security: ?string, body_id: ?int64,"
                "controlling_minor_faction_id: ?int64 }")
    t = odo('jsonlines://stations.json', url, dshape=ds)

    print("Creating indexes...")
    DBSession.execute("CREATE index index_stations_systemid_btree on stations(system_id)")
    mark_changed(DBSession())
    transaction.commit()
    DBSession.execute("CREATE index index_stations_btree on stations(id)")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")

    #
    # Listings
    #
    # TODO: Finish adding Listings
    if os.path.isfile('listings.csv'):
        if datetime.fromtimestamp(os.path.getmtime('listings.csv')) > datetime.today()-timedelta(days=7):
            print("Using cached listings.csv")
    else:
        print("Downloading listings.csv from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/listings.csv", stream=True)
        with open('listings.csv', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved listings.csv. Converting CSV to SQL.")
    url = str(engine.url) + "::" + Listing.__tablename__
    ds = dshape("var *{  id: ?int64, station_id: ?int64, commodity: ?int64, supply: ?int64, "
                "buy_price: ?int64, sell_price: ?int64, demand: ?int64, collected_at: ?int64 }")
    t = odo('listings.csv', url, dshape=ds)

    print("Creating indexes...")
    DBSession.execute("CREATE INDEX index_listings_stationid_btree on listings(station_id)")
    mark_changed(DBSession())
    transaction.commit()
main()
