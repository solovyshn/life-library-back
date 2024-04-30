from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'Books'

    ISBN = db.Column(db.String(10, 'Ukrainian_CI_AS'), primary_key=True)
    Book_Title = db.Column('Book-Title', db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Book_Author = db.Column('Book-Author', db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Year_Of_Publisher = db.Column('Year-Of-Publisher', db.Integer, nullable=False)
    Publisher = db.Column(db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Genre = db.Column(db.String(50, 'Ukrainian_CI_AS'), nullable=False)
    Description = db.Column(db.TEXT(2147483647, 'Ukrainian_CI_AS'), nullable=False)
    Average_rating = db.Column('Average-rating', db.DECIMAL(3, 1), nullable=False)
    Ratings_count = db.Column('Ratings-count', db.Integer, nullable=False)
    Image_URL_S = db.Column('Image-URL-S', db.String(collation='Ukrainian_CI_AS'), nullable=False)
    Image_URL_M = db.Column('Image-URL-M', db.String(collation='Ukrainian_CI_AS'), nullable=False)
    Image_URL_L = db.Column('Image-URL-L', db.String(collation='Ukrainian_CI_AS'), nullable=False)


t_OwnedBooks = db.Table(
    'OwnedBooks',
    Column('ISBN', db.String(10, 'Ukrainian_CI_AS'), nullable=False),
    Column('userID', db.Integer, nullable=False),
    Column('status', db.String(50, 'Ukrainian_CI_AS'), nullable=False),
    Column('rating', db.Integer),
    Column('update_date', db.Date, nullable=False),
    Column('secondUserID', db.Integer)
)


class User(db.Model):
    __tablename__ = 'Users'

    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Password = db.Column(db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Name = db.Column(db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Birthday = db.Column(db.Date, nullable=False)
    Region = db.Column(db.String(255, 'Ukrainian_CI_AS'), nullable=False)
    Avatar = db.Column(db.LargeBinary)
    
    @classmethod
    def email_exists(cls, email):
        return cls.query.filter_by(Email=email).first() is not None
    def __repr__(self):
        return '<User %r>' % self.yourName    
    def get_last_id(cls):
        last_user = cls.query.order_by(cls.userID.desc()).first()
        return last_user.id if last_user else None