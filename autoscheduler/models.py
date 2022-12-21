from sqlalchemy import Column, Integer, String 
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

class Qualification(Base):
    __tablename__ = 'quals'

    id = Column(Integer, primary_key=True)
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

    #ops_sup = Column('operations_supervisor', Boolean)
    #sof = Column('sof', Boolean)
    #rsu_controller = Column('rsu_controller', Boolean)
    #rsu_observer = Column('rsu_observer', Boolean)

    #pit_ip = Column(Boolean)

    #addresses = relationship(
    #    "Address", back_populates="user", cascade="all, delete-orphan"
    #)

    #def __repr__(self):
    #    return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
