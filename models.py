from sqlalchemy import Boolean, Column, DECIMAL, Date, ForeignKey, Integer, LargeBinary, String, TEXT, func, cast
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'Books'
    ISBN = Column(String(10, 'Ukrainian_CI_AS'), primary_key=True)
    Book_Title = Column('Book-Title', String(255, 'Ukrainian_CI_AS'), nullable=False)
    Book_Author = Column('Book-Author', String(255, 'Ukrainian_CI_AS'), nullable=False)
    Year_Of_Publisher = Column('Year-Of-Publisher', Integer, nullable=False)
    Publisher = Column(String(255, 'Ukrainian_CI_AS'), nullable=False)
    Genre = Column(String(50, 'Ukrainian_CI_AS'), nullable=False)
    Description = Column(TEXT(2147483647, 'Ukrainian_CI_AS'), nullable=False)
    Average_rating = Column('Average-rating', DECIMAL(3, 1), nullable=False)
    Ratings_count = Column('Ratings-count', Integer, nullable=False)
    Image_URL_S = Column('Image-URL-S', String(collation='Ukrainian_CI_AS'), nullable=False)
    Image_URL_M = Column('Image-URL-M', String(collation='Ukrainian_CI_AS'), nullable=False)
    Image_URL_L = Column('Image-URL-L', String(collation='Ukrainian_CI_AS'), nullable=False)
    @classmethod
    def searchBooks(crs, parameter):
        books = db.session.query(Book).filter(
            (Book.Book_Title.ilike(f"%{parameter}%")) |
            (Book.Book_Author.ilike(f"%{parameter}%")) |
            (Book.Genre.ilike(f"%{parameter}%")) |
            (Book.ISBN.ilike(f"%{parameter}%"))
        ).all()
        return books
    def get_all_books(cls, session):
        books_info = []
        books = session.query(cls).all()
        for book in books:
            info = {
                'ISBN': book.ISBN,
                'Book_Title': book.Book_Title,
                'Book_Author': book.Book_Author,
                'Year_Of_Publisher': book.Year_Of_Publisher,
                'Genre': book.Genre,
                'Average_rating': float(book.Average_rating),
                'Ratings_count': book.Ratings_count,
                'Image_URL_M': book.Image_URL_M
            }
            books_info.append(info)
        return books_info


t_OwnedBooks = db.Table(
    'OwnedBooks',
    Column('ISBN', String(10, 'Ukrainian_CI_AS'), ForeignKey('Books.ISBN'),  nullable=False),
    Column('userID', Integer, ForeignKey('Users.user_id'), nullable=False),
    Column('status_id', Integer, nullable=False),
    Column('rating', Integer),
    Column('update_date', Date, nullable=False),
    Column('secondUserID', Integer),
    Column('review', TEXT(2147483647, 'Ukrainian_CI_AS'))
)

class Region(db.Model):
    __tablename__ = 'Regions'
    region_id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(50, 'Ukrainian_CI_AS'), nullable=False)


class Shelf(db.Model):
    __tablename__ = 'Shelves'
    shelf_id = Column(Integer, primary_key=True)
    shelf_name = Column(String(50, 'Ukrainian_CI_AS'), nullable=False)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=True)
    PublicStatus = Column(Boolean, nullable=False)
    descriptiom = Column(String(255, 'Ukrainian_CI_AS'))

    @classmethod
    def get_shelf_id_by_name(cls, shelf_name):
        shelf = cls.query.filter_by(shelf_name=shelf_name).first()
        return shelf.shelf_id if shelf else None


class User(db.Model):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255, 'Ukrainian_CI_AS'), nullable=False)
    password = Column(String(255, 'Ukrainian_CI_AS'), nullable=False)
    name = Column(String(255, 'Ukrainian_CI_AS'), nullable=False)
    birthday = Column(Date, nullable=False)
    region_id = Column(Integer, ForeignKey('Regions.region_id'), nullable=False)
    Avatar = Column(LargeBinary)
    PublicLibrary = Column(Boolean, nullable=False)
    LibraryType = Column(Boolean, nullable=False)
    rated_books = relationship("Book", secondary=t_OwnedBooks)
    @classmethod
    def email_exists(cls, Email):
        return cls.query.filter_by(email=Email).first() is not None
    def repr(self):
        return '<User %r>' % self.yourName    
    def getRegion(self):
        return self.region_id
    def get_last_id(cls):
        last_user = cls.query.order_by(cls.userID.desc()).first()
        return last_user.id if last_user else None
    def get_last_added_book(cls, current_user_id):
        last_added_book_query = db.session.query(
            t_OwnedBooks.c.update_date,
            Book.Book_Title,
            Book.Book_Author,
            Book.Image_URL_M,
            t_OwnedBooks.c.ISBN
        ).join(
            Book, t_OwnedBooks.c.ISBN == Book.ISBN
        ).filter(
            t_OwnedBooks.c.userID == current_user_id,
            t_OwnedBooks.c.status_id == 5
        ).order_by(
            t_OwnedBooks.c.update_date.desc()
        )
        last_added_book = last_added_book_query
        return last_added_book
    def get_shelves_covers(cls, current_user_id):
        shelves_covers = db.session.query(
            t_OwnedBooks.c.status_id,
            func.first_value(t_OwnedBooks.c.update_date).over(
                partition_by=t_OwnedBooks.c.status_id,
                order_by=t_OwnedBooks.c.update_date
            ).label('first_update_date')
        ).filter(
            t_OwnedBooks.c.userID == current_user_id
        ).group_by(
            t_OwnedBooks.c.status_id,
            t_OwnedBooks.c.update_date  
        ).subquery()
        last_added_books_query = db.session.query(
            func.distinct(Shelf.shelf_name),
            Book.Image_URL_L
        ).select_from(
            t_OwnedBooks
        ).join(
            shelves_covers, (t_OwnedBooks.c.status_id == shelves_covers.c.status_id) & (t_OwnedBooks.c.update_date == shelves_covers.c.first_update_date)
        ).join(
            Shelf, t_OwnedBooks.c.status_id == Shelf.shelf_id
        ).join(
            Book, t_OwnedBooks.c.ISBN == Book.ISBN
        ).filter(
            t_OwnedBooks.c.userID == current_user_id
        ).all()
        result = [[shelf_name, cover] for shelf_name, cover in last_added_books_query]
        return result
    def get_shelves_with_books(cls, user_id):
        user_shelves = db.session.query(Shelf).filter(
            (Shelf.user_id == user_id) | (Shelf.user_id == None)
        ).all()
        print(user_shelves)

        shelves_with_books = []

        for shelf in user_shelves:
            books_in_shelf = db.session.query(
                Book.ISBN,
                Book.Book_Title,
                Book.Book_Author,
                Book.Genre,
                Book.Image_URL_M,
                t_OwnedBooks.c.update_date,
                t_OwnedBooks.c.secondUserID,
                User.name.label('second_user_name')
            ).join(
                t_OwnedBooks, t_OwnedBooks.c.ISBN == Book.ISBN
            ).outerjoin(
                User, User.user_id == t_OwnedBooks.c.secondUserID
            ).filter(
                t_OwnedBooks.c.userID == user_id,
                t_OwnedBooks.c.status_id == shelf.shelf_id
            ).all()

            books_data = [{
                'ISBN': book.ISBN,
                'title': book.Book_Title,
                'author': book.Book_Author,
                'genre': book.Genre,
                'image_url': book.Image_URL_M,
                'update_date': book.update_date.strftime('%d %B, %Y') if book.update_date else None,
                'second_user_name': book.second_user_name if book.secondUserID else None,
                'second_user_id': book.secondUserID if book.secondUserID else None
            } for book in books_in_shelf]

            shelves_with_books.append({
                'shelf_id': shelf.shelf_id,
                'shelf_name': shelf.shelf_name,
                'books': books_data
            })

        return shelves_with_books
    def bookOwners(crs, books, userID):
        user = User.query.filter_by(user_id=userID).first()
        result = []
        for book in books:
            users_with_book = db.session.query(User).join(t_OwnedBooks, User.user_id == t_OwnedBooks.c.userID).filter(
                t_OwnedBooks.c.ISBN == book.ISBN,
                User.PublicLibrary == True,
                User.user_id != userID,
                User.region_id == user.getRegion(),
                t_OwnedBooks.c.status_id != 4
            ).all()
            users_info = [{'user_id': user.user_id, 'email': user.email, 'name': user.name} for user in users_with_book]
            
            book_info = {
                'ISBN': book.ISBN,
                'title': book.Book_Title,
                'author': book.Book_Author,
                'genre': book.Genre,
                'image_url': book.Image_URL_M,
                'users': users_info
            }
            result.append(book_info)
        return result
    def get_shelves_and_book_info(cls, user_id, isbn):
        user_shelves = db.session.query(Shelf).filter(
            (Shelf.user_id == user_id) | (Shelf.user_id == None)
        ).all()

        shelves_data = [{
            'shelf_id': shelf.shelf_id,
            'shelf_name': shelf.shelf_name
        } for shelf in user_shelves]        
        book_info = db.session.query(
            Book.ISBN,
            Book.Book_Title,
            Book.Book_Author,
            Book.Genre,
            Book.Image_URL_L,
            Book.Year_Of_Publisher,
            Book.Publisher,
            Book.Description,
            Book.Average_rating,
            Book.Ratings_count
        ).filter(Book.ISBN == isbn).first()

        if book_info:
            book_details = {
                'ISBN': book_info.ISBN,
                'title': book_info.Book_Title,
                'author': book_info.Book_Author,
                'genre': book_info.Genre,
                'image_url': book_info.Image_URL_L,
                'year': book_info.Year_Of_Publisher,
                'publisher': book_info.Publisher,
                'description': book_info.Description,
                'average_rating': book_info.Average_rating,
                'ratings_count': book_info.Ratings_count
            }
            book_shelves = db.session.query(
                Shelf.shelf_name
            ).join(
                t_OwnedBooks, Shelf.shelf_id == t_OwnedBooks.c.status_id
            ).filter(
                t_OwnedBooks.c.userID == user_id,
                t_OwnedBooks.c.ISBN == isbn
            ).all()

            book_details['shelf_names'] = [book_shelf.shelf_name for book_shelf in book_shelves]
            
            reviews_data = db.session.query(
                t_OwnedBooks.c.review,
                t_OwnedBooks.c.update_date,
                User.name
            ).join(
                User, t_OwnedBooks.c.userID == User.user_id
            ).filter(
                t_OwnedBooks.c.ISBN == isbn,
                func.length(cast(t_OwnedBooks.c.review, String)) > 0
            ).all()

            reviews = [{
                'review': review.review,
                'username': review.name,
                'date': review.update_date.strftime("%d %B, %Y")
            } for review in reviews_data]

            book_details['reviews'] = reviews

        else:
            book_details = None
        return {
            'shelves': shelves_data,
            'book_details': book_details
        }
    def get_book_ratings(cls, session, user_id):
        user = session.query(cls).get(user_id)
        if user:
            user_books_info = []
            for book in user.rated_books:
                rating = session.query(t_OwnedBooks.c.rating).\
                    filter_by(ISBN=book.ISBN, userID=user_id).\
                    filter(t_OwnedBooks.c.rating.isnot(None)).\
                    scalar()
                if rating is not None:
                    info = {
                        'ISBN': book.ISBN,
                        'rating': rating
                    }
                else:
                    continue
                user_books_info.append(info)
            return user_books_info
        else:
            return None


    