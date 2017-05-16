from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Float,
    Boolean,
    ForeignKey
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Body(Base):
    __tablename__ = 'bodies'
    id = Column(Integer, primary_key=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    name = Column(Text)
    system_id = Column(BigInteger, ForeignKey('systems.id'))
    group_id = Column(Integer)
    group_name = Column(Text)
    type_id = Column(BigInteger)
    type_name = Column(Text)
    distance_to_arrival = Column(BigInteger)
    full_spectral_class = Column(Text)
    spectral_class = Column(Text)
    spectral_sub_class = Column(Text)
    luminosity_class = Column(Text)
    luminosity_sub_class = Column(Text)
    surface_temperature = Column(BigInteger)
    is_main_star = Column(Boolean)
    age = Column(BigInteger)
    solar_masses = Column(Float)
    solar_radius = Column(Float)
    catalogue_gliese_id = Column(Text)
    catalogue_hipp_id = Column(Text)
    catalogue_hd_id = Column(Text)
    volcanism_type_id = Column(BigInteger)
    volcanism_type_name = Column(Text)
    atmosphere_type_id = Column(BigInteger)
    atmosphere_type_name = Column(Text)
    terraforming_state_id = Column(BigInteger)
    terraforming_state_name = Column(Text)
    earth_masses = Column(Float)
    radius = Column(BigInteger)
    gravity = Column(Float)
    surface_pressure = Column(BigInteger)
    orbital_period = Column(Float)
    semi_major_axis = Column(Float)
    orbital_eccentricity = Column(Float)
    orbital_inclination = Column(Float)
    arg_of_periapsis = Column(Float)
    rotational_period = Column(Float)
    is_rotational_period_tidally_locked = Column(Boolean)
    axis_tilt = Column(Float)
    eg_id = Column(BigInteger)
    belt_moon_masses = Column(Float)
    ring_type_id = Column(BigInteger)
    ring_type_name = Column(Text)
    ring_mass = Column(BigInteger)
    ring_inner_radius = Column(Float)
    ring_outer_radius = Column(Float)
    rings = Column(JSONB)
    atmosphere_composition = Column(JSONB)
    solid_composition = Column(JSONB)
    materials = Column(JSONB)
    is_landable = Column(Boolean)
    stations = relationship("Station")


class Faction(Base):
    __tablename__ = 'factions'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    updated_at = Column(BigInteger)
    government_id = Column(BigInteger)
    government= Column(Text)
    allegiance_id = Column(BigInteger)
    allegiance = Column(Text)
    state_id = Column(Integer)
    state = Column(Text)
    home_system_id = Column(BigInteger)
    is_player_faction = Column(Boolean)


class Station(Base):
    __tablename__ = 'stations'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    system_id = Column(BigInteger)
    updated_at = Column(BigInteger)
    max_landing_pad_size = Column(Text)
    distance_to_star = Column(BigInteger)
    government_id = Column(Integer)
    government = Column(Text)
    allegiance_id = Column(Integer)
    allegiance = Column(Text)
    state_id = Column(Integer)
    state = Column(Text)
    type_id = Column(Integer)
    type = Column(Text)
    has_blackmarket = Column(Boolean)
    has_market = Column(Boolean)
    has_refuel = Column(Boolean)
    has_repair = Column(Boolean)
    has_rearm = Column(Boolean)
    has_outfitting = Column(Boolean)
    has_shipyard = Column(Boolean)
    has_docking = Column(Boolean)
    has_commodities = Column(Boolean)
    import_commodities = Column(JSONB)
    export_commodities = Column(JSONB)
    prohibited_commodities = Column(JSONB)
    economies = Column(JSONB)
    shipyard_updated_at = Column(BigInteger)
    outfitting_updated_at = Column(BigInteger)
    market_updated_at = Column(BigInteger)
    is_planetary = Column(Boolean)
    selling_ships = Column(JSONB)
    selling_modules = Column(JSONB)
    settlement_size_id = Column(Integer)
    settlement_size = Column(Text)
    settlement_security_id = Column(Integer)
    settlement_security = Column(Text)
    body_id = Column(BigInteger, ForeignKey('bodies.id'))
    controlling_minor_faction_id = Column(BigInteger, ForeignKey('factions.id'))
    listings = relationship("Listing")


class Listing(Base):
    __tablename__ = 'listings'
    id = Column(BigInteger, primary_key=True)
    station_id = Column(BigInteger, ForeignKey('stations.id'))
    commodity = Column(Integer)
    supply = Column(Integer)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
    demand = Column(Integer)
    collected_at = Column(BigInteger)


class PopulatedSystem(Base):
    __tablename__ = 'populated_systems'
    id = Column(Integer, primary_key=True)
    edsm_id = Column(Integer)
    name = Column(Text)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    population = Column(BigInteger)
    is_populated = Column(Boolean)
    government_id = Column(Integer)
    government = Column(Text)
    allegiance_id = Column(Integer)
    allegiance = Column(Text)
    state_id = Column(Integer)
    state = Column(Text)
    security_id = Column(Integer)
    security = Column(Text)
    primary_economy_id = Column(Integer)
    primary_economy = Column(Text)
    power = Column(Text)
    power_state = Column(Text)
    power_state_id = Column(Integer)
    needs_permit = Column(Boolean)
    updated_at = Column(BigInteger)
    simbad_ref = Column(Text)
    controlling_minor_faction_id = Column(Integer, ForeignKey('factions.id'))
    controlling_minor_faction = Column(Text)
    reserve_type_id = Column(Integer)
    reserve_type = Column(Text)
    minor_faction_presences = Column(JSONB)
    factions = relationship("Faction")


class System(Base):
    __tablename__ = 'systems'
    id = Column(BigInteger, primary_key=True)
    edsm_id = Column(BigInteger)
    name = Column(Text)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    population = Column(BigInteger)
    is_populated = Column(Integer)
    government_id = Column(Integer)
    government = Column(Text)
    allegiance_id = Column(Integer)
    allegiance = Column(Text)
    state_id = Column(Integer)
    state = Column(Text)
    security_id = Column(Integer)
    security = Column(Text)
    primary_economy_id = Column(Integer)
    primary_economy = Column(Text)
    power = Column(Text)
    power_state = Column(Text)
    power_state_id = Column(Integer)
    needs_permit = Column(Integer)
    updated_at = Column(BigInteger)
    simbad_ref = Column(Text)
    controlling_minor_faction_id = Column(Integer)
    controlling_minor_faction = Column(Text)
    reserve_type_id = Column(Integer)
    reserve_type = Column(Text)
    bodies = relationship("Body")


    def __init__(self, request):
        pass
