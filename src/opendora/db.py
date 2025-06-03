from pathlib import Path
from opendora.model import *
from sqlmodel import SQLModel, create_engine

# Create the path to the db
db_path = Path("opendora.sqlite").absolute()

print(db_path)

db_url = f"sqlite:///{db_path}"

engine = create_engine(db_url)
SQLModel.metadata.create_all(engine)
