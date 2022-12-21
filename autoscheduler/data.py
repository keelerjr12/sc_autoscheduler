from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/sparkcell")
session = Session(engine)