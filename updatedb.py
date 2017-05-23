import os, sys, transaction, requests

from odo import odo, dshape

import requests
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config, sql, orm, schema
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
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    print("Beginning update.")
    PopulatedSystem.__table__.drop(engine)
    Station.__table__.drop(engine)
    Faction.__table__.drop(engine)
    Listing.__table__.drop(engine)
    PopulatedSystem.__table__.create(engine)
    Station.__table__.create(engine)
    Faction.__table__.create(engine)
    Listing.__table__.create(engine)
    mark_changed(DBSession())
    transaction.commit()

    #
    # Factions
    #
    print("Updating factions...")
    print("Downloading factions.jsonl from EDDB.io...")
    r = requests.get("https://eddb.io/archive/v5/factions.jsonl", stream=True)
    with open('factions.json', 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    print("Saved factions.json. Dropping and updating.")
    url = str(engine.url) + "::" + Faction.__tablename__
    ds = dshape("var *{  id: ?int64,  name: ?string,  updated_at: ?int64,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string, home_system_id: ?int64,  "
                "is_player_faction: ?bool }")
    t = odo('jsonlines://factions.json', url, dshape=ds)
    print("Done!")
    mark_changed(DBSession())
    transaction.commit()

    #
    # Populated systems
    #
    print("Downloading systems_populated.jsonl from EDDB.io...")
    r = requests.get("https://eddb.io/archive/v5/systems_populated.jsonl", stream=True)
    with open('systems_populated.json', 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    print("Saved systems_populated.json. Dropping and updating.")
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
    print("Done!")

    #
    # Stations
    #
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
                "selling_modules: ?json, settlement_size_id: ?string, settlement_size: ?int64, "
                "settlement_security_id: ?int64, settlement_security: ?string, body_id: ?int64,"
                "controlling_minor_faction_id: ?int64 }")
    t = odo('jsonlines://stations.json', url, dshape=ds)

    #
    # Systems
    #
    print("Downloading systems_recently.csv from EDDB.io...")
    r = requests.get("https://eddb.io/archive/v5/systems_recently.csv", stream=True)
    with open('systems_recently.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    print("Saved systems_recently.csv. Creating temporary table and importing.")
    DBSession.execute("CREATE TEMP TABLE systems_tmp (LIKE systems)")
    url = str(engine.url) + "::systems_tmp"
    ds = dshape("var *{  id: ?int64,  edsm_id: ?int64,  name: ?string,  x: ?float64,  y: ?float64,  "
                "z: ?float64,  population: ?int64,  is_populated: ?bool,  government_id: ?int64,  "
                "government: ?string,  allegiance_id: ?int64,  allegiance: ?string,  "
                "state_id: ?int64,  state: ?string,  security_id: ?float64,  security: ?string,  "
                "primary_economy_id: ?float64,  primary_economy: ?string,  power: ?string,  "
                "power_state: ?string,  power_state_id: ?string,  needs_permit: ?bool,  "
                "updated_at: ?int64,  simbad_ref: ?string,  controlling_minor_faction_id: ?string,  "
                "controlling_minor_faction: ?string,  reserve_type_id: ?float64,  reserve_type: ?string  }")
    t = odo('systems_recently.csv', url, dshape=ds)
    print("Updating systems...")
    DBSession.execute("INSERT INTO systems(id, edsm_id, name, x, y, z, population, is_populated, government_id, "
                      "government, allegiance_id, allegiance, state_id, state, security_id, security, "
                      "primary_economy_id, primary_economy, power, power_state, power_state_id, needs_permit, "
                      "updated_at, simbad_ref, controlling_minor_faction_id, controlling_minor_faction, "
                      "reserve_type_id, reserve_type) SELECT id, edsm_id, name, x, y, z, population, is_populated, "
                      "government_id, government, allegiance_id, allegiance, state_id, state, security_id, security, "
                      "primary_economy_id, primary_economy, power, power_state, power_state_id, needs_permit, "
                      "updated_at, simbad_ref, controlling_minor_faction_id, controlling_minor_faction, "
                      "reserve_type_id, reserve_type from systems_tmp ON CONFLICT DO UPDATE "
                      "SET edsm_id = EXCLUDED.edsm_id, name = EXCLUDED.name, x = EXCLUDED.x, "
                      "y = EXCLUDED.y, z = EXCLUDED.z, population = EXCLUDED.population, "
                      "is_populated = EXCLUDED.population, government_id = EXCLUDED.government_id, "
                      "government = EXCLUDED.government, allegiance_id = EXCLUDED.allegiance_id, "
                      "allegiance = EXCLUDED.allegiance, state_id = EXCLUDED.state_id, "
                      "state = EXCLUDED.state, security_id = EXCLUDED.security_id, security = EXCLUDED.security, "
                      "primary_economy_id = EXCLUDED.primary_economy_id, primary_economy = EXCLUDED.primary_economy, "
                      "power = EXCLUDED.power, power_state = EXCLUDED.power_state, power_state_id = "
                      "EXCLUDED.power_state_id, needs_permit = EXCLUDED.needs_permit, updated_at = "
                      "EXCLUDED.updated_at, simbad_ref = EXCLUDED.simbad_ref,"
                      "controlling_minor_faction_id = EXCLUDED.controlling_minor_faction_id, "
                      "reserve_type_id = EXCLUDED.reserve_type_id, reserve_type = EXCLUDED.reserve_type")
    mark_changed(DBSession())
    transaction.commit()
    print("Done!")

    #
    # TODO: Update listings
    #
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
    DBSession.execute("CREATE INDEX index_listings_stationid_btree ON listings(station_id)")
    mark_changed(DBSession())
    transaction.commit()


main()
