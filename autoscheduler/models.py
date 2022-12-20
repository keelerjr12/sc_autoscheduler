from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Pilot(Base):
    __tablename__ = "pilots"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    ausm_tier = Column(Integer)

    #addresses = relationship(
    #    "Address", back_populates="user", cascade="all, delete-orphan"
    #)

    #def __repr__(self):
    #    return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"