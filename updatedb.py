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
    DBSession.execute("DELETE FROM factions")
    mark_changed(DBSession())
    transaction.commit()
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
    DBSession.execute("DELETE FROM populated_systems")
    mark_changed(DBSession())
    transaction.commit()
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
    # TODO: Update bodies
    #

    #
    # TODO: Update systems
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
    DBSession.execute("INSERT INTO systems SELECT * FROM systems_tmp ON CONFLICT (id) DO UPDATE "
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
    #
    # TODO: Update stations
    #

    #
    # TODO: Update listings
    #

main()
