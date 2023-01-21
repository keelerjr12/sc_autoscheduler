from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/sparkcell")
Session = sessionmaker(engine)

# Dependency
def get_db():
    db = Session()

    try:
        yield db
    finally:
        db.close()
