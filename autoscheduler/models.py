from sqlalchemy import Column, DateTime, Integer, String 
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'org'

    id = Column(Integer, primary_key=True)
    name = Column(String)

PilotOrganization = Table(
    "pilot_org",
    Base.metadata,
    Column("pilot_id", ForeignKey("pilot.id"), primary_key=True),
    Column("org_id", ForeignKey("org.id"), primary_key=True),
)

class QualificationType(Base):
    __tablename__ = 'qual_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Qualification(Base):
    __tablename__ = 'qual'

    id = Column(Integer, primary_key=True)

    type_id = Column(Integer, ForeignKey('qual_type.id'))
    type = relationship('QualificationType')

    name = Column(String)

PilotQualification = Table(
    "pilot_qual",
    Base.metadata,
    Column("pilot_id", ForeignKey("pilot.id"), primary_key=True),
    Column("qual_id", ForeignKey("qual.id"), primary_key=True),
)

class Pilot(Base):
    __tablename__ = 'pilot'

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    ausm_tier = Column(Integer)
    assigned_org = relationship('Organization', secondary=PilotOrganization)

    quals = relationship('Qualification', secondary=PilotQualification)

class ShellLine(Base):
    __tablename__ = 'shell_line'

    id = Column(Integer, primary_key=True)
    num = Column(Integer)
    start_date_time = Column(DateTime)

    org_id = Column(Integer, ForeignKey('org.id'))
    org = relationship('Organization')

    go = Column('fly_go', Integer)

class DutyType(Base):
    __tablename__ = 'duty_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Duty(Base):
    __tablename__ = 'duty'

    id = Column(Integer, primary_key=True)

    duty_type_id = Column(Integer, ForeignKey('duty_type.id'))
    duty_type = relationship('DutyType')

    name = Column(String)

class ShellDuty(Base):
    __tablename__ = 'shell_duty'

    id = Column(Integer, primary_key=True)

    duty_id = Column(Integer, ForeignKey('duty.id'))
    duty = relationship('Duty')

    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime)

class AbsenceRequestDto(Base):
    __tablename__ = 'absence_request'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('pilot.id'))
    person = relationship('Pilot')

    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime)
    occur_start_date_time = Column(DateTime)
    occur_end_date_time = Column(DateTime)

    day_of_week_ptn = Column(Integer)