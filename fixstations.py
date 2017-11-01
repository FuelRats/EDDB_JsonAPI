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
    print("Beginning stationfix.")
    if os.path.isfile('stations.json'):
        if datetime.fromtimestamp(os.path.getmtime('stations.json')) > datetime.today() - timedelta(days=7):
            print("Using cached stations.json")
    else:
        print("Downloading stations.jsonl from EDDB.io...")
        r = requests.get("https://eddb.io/archive/v5/stations.jsonl", stream=True)
        with open('stations.json', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        print("Saved stations.json. Creating temporary table and importing.")
    DBSession.execute("CREATE TABLE stations_tmp (LIKE stations)")
    url = str(engine.url) + "::stations_tmp"
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
