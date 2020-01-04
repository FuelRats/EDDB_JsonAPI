from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Float,
    Boolean,
    DateTime,
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


class PopulatedSystem(Base):
    __tablename__ = 'populated_systems'
    id = Column(BigInteger, primary_key=True, doc="Internal system ID")
    id64 = Column(BigInteger, doc="64-bit system ID")
    name = Column(Text, doc="System name")
    coords = Column(JSONB, doc="System coordinates, as a JSON blob with X,Y and Z coordinates as floats.")
    controllingFaction = Column(JSONB, doc="Controlling faction, in a JSON blob")
    date = Column(DateTime, doc="DateTime of last update to this system")
    date.info.update({'pyramid_jsonapi': {'visible': False}})


class System(Base):
    __tablename__ = 'systems'
    id = Column(BigInteger, primary_key=True)
    id64 = Column(BigInteger)
    name = Column(Text)
    coords = Column(JSONB)
    date = Column(DateTime)
    date.info.update({'pyramid_jsonapi': {'visible': False}})


class Station(Base):
    __tablename__ = 'stations'
    id = Column(BigInteger, primary_key=True)
    marketId = Column(BigInteger)
    type = Column(Text)
    name = Column(Text)
    distanceToArrival = Column(Float)
    allegiance = Column(Text)
    government = Column(Text)
    economy = Column(Text)
    haveMarket = Column(Boolean)
    haveShipyard = Column(Boolean)
    haveOutfitting = Column(Boolean)
    otherServices = Column(JSONB)
    updateTime = Column(JSONB)
    updateTime.info.update({'pyramid_jsonapi': {'visible': False}})
    systemId = Column(BigInteger)
    systemId64 = Column(BigInteger)
    systemName = Column(Text)


class Body(Base):
    __tablename__ = 'bodies'
    id = Column(BigInteger, primary_key=True)
    id64 = Column(BigInteger)
    bodyId = Column(Integer)
    name = Column(Text)
    discovery = Column(JSONB)
    type = Column(Text)
    subType = Column(Text)
    offset = Column(Integer)
    parents = Column(JSONB)
    distanceToArrival = Column(Float)
    isLandable = Column(Boolean)
    gravity = Column(Float)
    earthMasses = Column(Float)
    radius = Column(Float)
    surfaceTemperature = Column(Float)
    surfacePressure = Column(Float)
    volcanismType = Column(Text)
    atmosphereType = Column(Text)
    atmosphereComposition = Column(JSONB)
    terraformingState = Column(Text)
    orbitalPeriod = Column(Float)
    semiMajorAxis = Column(Float)
    orbitalEccentricity = Column(Float)
    orbitalInclination = Column(Float)
    argOfPeriapsis = Column(Float)
    rotationalPeriod = Column(Float)
    rotationalPeriodTidallyLocked = Column(Boolean)
    axialTilt = Column(Float)
    rings = Column(JSONB)
    materials = Column(JSONB)
    updateTime = Column(DateTime)
    updateTime.info.update({'pyramid_jsonapi': {'visible': False}})
    systemId = Column(BigInteger)
    systemId64 = Column(BigInteger)
    systemName = Column(Text)


class Star(Base):
    __tablename__ = 'stars'
    id = Column(BigInteger, primary_key=True)
    id64 = Column(BigInteger)
    bodyId = Column(Integer)
    name = Column(Text)
    discovery = Column(JSONB)
    type = Column(Text)
    subType = Column(Text)
    offset = Column(Integer)
    parents = Column(JSONB)
    distanceToArrival = Column(Float)
    isMainStar = Column(Boolean)
    isScoopable = Column(Boolean)
    age = Column(BigInteger)
    luminosity = Column(Text)
    absoluteMagnitude = Column(Float)
    solarMasses = Column(Float)
    solarRadius = Column(Float)
    surfaceTemperature = Column(BigInteger)
    volcanismType = Column(Text)
    atmosphereType = Column(Text)
    terraformingState = Column(Text)
    orbitalPeriod = Column(Float)
    semiMajorAxis = Column(Float)
    orbitalEccentricity = Column(Float)
    orbitalInclination = Column(Float)
    argOfPeriapsis = Column(Float)
    rotationalPeriod = Column(Float)
    rotationalPeriodTidallyLocked = Column(Boolean)
    axialTilt = Column(Float)
    belts = Column(JSONB)
    updateTime = Column(DateTime)
    updateTime.info.update({'pyramid_jsonapi': {'visible': False}})
    systemId = Column(BigInteger)
    systemId64 = Column(BigInteger)
    systemName = Column(Text)


class Landmark(Base):
    __tablename__ = 'landmarks'
    name = Column(Text, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)


class Permits(Base):
    __tablename__ = 'permit_systems'
    id64 = Column(BigInteger)

