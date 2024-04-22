from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Book, User

# Create an engine and bind the session
engine = create_engine('mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
Session = sessionmaker(bind=engine)
session = Session()

# Query the database using the generated classes
result = session.query(Book).filter(Book.Year_Of_Publication == 2003).all()
print(result)