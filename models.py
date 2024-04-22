# coding: utf-8
from sqlalchemy import Column, DECIMAL, Date, Integer, String, TEXT, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Book(Base):
    __tablename__ = 'Books'

    ISBN = Column(String(10, 'Latin1_General_CI_AS'), primary_key=True)
    Title = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    Author = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    Year_Of_Publication = Column('Year-Of-Publication', Integer)
    Publisher = Column(String(255, 'Latin1_General_CI_AS'))
    Genre = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    Description = Column(TEXT(2147483647, 'Latin1_General_CI_AS'))
    Average_rating = Column(DECIMAL(3, 1))
    Ratings_count = Column(Integer)
    Image_URL_S = Column('Image-URL-S', String(255, 'Latin1_General_CI_AS'))
    Image_URL_M = Column('Image-URL-M', String(255, 'Latin1_General_CI_AS'))
    Image_URL_L = Column('Image-URL-L', String(255, 'Latin1_General_CI_AS'))


t_OwnedBooks = Table(
    'OwnedBooks', metadata,
    Column('userID', Integer, nullable=False),
    Column('ISBN', String(10, 'Latin1_General_CI_AS'), nullable=False),
    Column('status', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('rating', Integer)
)


class User(Base):
    __tablename__ = 'Users'

    userID = Column(Integer, primary_key=True)
    email = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    password = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    name = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    surname = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
    birthday = Column(Date, nullable=False)
    city = Column(String(255, 'Latin1_General_CI_AS'), nullable=False)
