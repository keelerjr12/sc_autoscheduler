from sqlalchemy import Column, DateTime, Integer, String 
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'orgs'

    id = Column(Integer, primary_key=True)
    name = Column(String)

PilotOrganization = Table(
    "pilots_orgs",
    Base.metadata,
    Column("pilot_id", ForeignKey("pilots.id"), primary_key=True),
    Column("org_id", ForeignKey("orgs.id"), primary_key=True),
)

class QualificationType(Base):
    __tablename__ = 'qual_types'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Qualification(Base):
    __tablename__ = 'quals'

    id = Column(Integer, primary_key=True)

    type_id = Column(Integer, ForeignKey('qual_types.id'))
    type = relationship('QualificationType')

    name = Column(String)

PilotQualification = Table(
    "pilots_quals",
    Base.metadata,
    Column("pilot_id", ForeignKey("pilots.id"), primary_key=True),
    Column("qual_id", ForeignKey("quals.id"), primary_key=True),
)

class Pilot(Base):
    __tablename__ = "pilots"

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    ausm_tier = Column(Integer)
    assigned_org = relationship('Organization', secondary=PilotOrganization)

    quals = relationship('Qualification', secondary=PilotQualification)

class ShellLine(Base):
    __tablename__ = "shell_lines"

    id = Column(Integer, primary_key=True)
    num = Column(Integer)
    start_date_time = Column(DateTime)

    org_id = Column(Integer, ForeignKey('orgs.id'))
    org = relationship('Organization')

    go = Column('fly_go', Integer)