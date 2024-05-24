from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import db, Book  # Assuming your Flask-SQLAlchemy db instance is named 'db' and Book model is defined in 'app.py'
import csv

# Define your database connection string
connection_string = 'mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL Server&trusted_connection=yes'

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Bind the engine to the metadata
db.metadata.bind = engine

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Open and read the CSV file
with open('BooksCleaned_editing.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        try:
            data_to_insert = {
                'ISBN': row[0],
                'Book_Title': row[1],
                'Book_Author': row[2],
                'Year_Of_Publisher': int(row[3]),  # Convert to integer if needed
                'Publisher': row[4],
                'Genre': row[5],
                'Description': row[6],
                'Average_rating': float(row[7]),  # Convert to float if needed
                'Ratings_count': int(row[8]),  # Convert to integer if needed
                'Image_URL_S': row[9],
                'Image_URL_M': row[10],
                'Image_URL_L': row[11]
            }
            # Insert data into the table using SQLAlchemy
            book = Book(**data_to_insert)
            session.add(book)
        except UnicodeDecodeError:
            print("Skipping line due to decoding error:", row)

# Commit the changes and close the session
session.commit()
session.close()