from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import db, Region  # Assuming Books is the correct class name in models.py
import json

# Define your database connection string
connection_string = 'mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL Server&trusted_connection=yes'

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Bind the engine to the metadata
db.metadata.bind = engine

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

with open("regions.json") as f:
    json_str = f.read()

# Parse the JSON string using json.loads()
region_data = json.loads(json_str)['regions']

for regionName in region_data:
    region = Region(region_name=regionName)
    session.add(region)


# Commit the changes and close the session
session.commit()
session.close()