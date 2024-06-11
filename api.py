import pandas as pd
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin  
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
from models import User, Region,  db, Book, Shelf
from recommendations_prediction import predict_recommendations
from sqlalchemy import text

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/register', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
@jwt_required
def register():
    data = request.get_json()

    if 'yourName' not in data or 'yourEmail' not in data or 'yourPassword' not in data or 'region' not in data or 'birthday' not in data or 'LibraryType' not in data or 'isPublic' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    if User.email_exists(data['yourEmail']):
        return jsonify({'error': 'Email already exists'}), 409 

    new_user = User(name=data['yourName'], email=data['yourEmail'], password=data['yourPassword'], birthday=data['birthday'], region_id=data['region'], PublicLibrary=data['isPublic'], LibraryType=data['LibraryType'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 200

@api_blueprint.route('/login', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def login():
    data = request.get_json()
    if 'yourEmail' not in data or 'yourPassword' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    email = data['yourEmail']
    password = data['yourPassword']
    user = User.query.filter_by(email=email).first()
    if user:
        if user.password == password:
            access_token = create_access_token(identity=user.user_id)
            return jsonify({'message': 'User logged in successfully', 'id': user.user_id, 'access_token': access_token}), 200
        else:
            return jsonify({'error': 'Incorrect password'}), 401
    else:
        return jsonify({'error': 'User with this email doesn\'t exist'}), 404

@api_blueprint.route('/regions', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type'])
def getRegions():
    regions = Region.query.all()
    regions_data = [{'id': region.region_id, 'name': region.region_name} for region in regions]
    return jsonify(regions_data)


@api_blueprint.route('/accountInfo/<int:userID>', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type'])
@jwt_required()
def getAccountInfo(userID):
    current_user_id = get_jwt_identity()
    if current_user_id != userID:
        return jsonify(message=userID), 401
    user = User.query.filter_by(user_id=current_user_id).first()
    if not user:
        return jsonify(message='User not found'), 404

    region_info = Region.query.with_entities(Region.region_name).filter_by(region_id=user.region_id).first()
    region_name = region_info[0] if region_info else None
    birth_date = user.birthday
    current_date = datetime.now()
    age = current_date.year - birth_date.year
    if current_date.month < birth_date.month or \
        (current_date.month == birth_date.month and current_date.day < birth_date.day):
            age -= 1

    birthday = birth_date.strftime("%d.%m.%Y")
    user_info = {
        'email': user.email,
        'userName': user.name,
        'birthday': birthday,
        'age': age,
        'region': region_name,
        'Avatar': user.Avatar,
        'PublicLibrary': user.PublicLibrary,
        'LibraryType': user.LibraryType,
    }
    last_added_book = User.get_last_added_book(User, current_user_id=current_user_id)
    if last_added_book == None:
        return jsonify({'error': 'No book found for the specified conditions'}), 404
    readings=[]
    for book in last_added_book:
        reading={}
        reading = {
            'update_date':book.update_date,
            'book_title': book.Book_Title,
            'book_author': book.Book_Author,
            'image_url': book.Image_URL_M,
            'ISBN': book.ISBN
        } 
        reading['update_date'] = reading['update_date'].strftime("%d %B, %Y")
        readings.append(reading)
    shelves = User.get_shelves_covers(User, current_user_id=current_user_id)

    recommendations = predict_recommendations(current_user_id)
    if recommendations is None:
        recommendations_dict=None
    elif isinstance(recommendations, pd.DataFrame):
        recommendations_dict = recommendations.to_dict(orient='records')
    else:
        recommendations_dict=None
        print("Recommendations are neither None nor a DataFrame.")

    accountInfo = {
        'user_info': user_info,
        'currentlyReading': readings,
        'recommendations': recommendations_dict if recommendations_dict else None,
        'shelves': shelves
    }
    return jsonify(accountInfo), 200

@api_blueprint.route('/anotherAccountInfo/<int:elseUserID>', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type'])
@jwt_required()
def getAnotherAccountInfo(elseUserID):
    print(elseUserID)
    user = User.query.filter_by(user_id=elseUserID).first()
    if not user:
        return jsonify(message='User not found'), 404

    region_info = Region.query.with_entities(Region.region_name).filter_by(region_id=user.region_id).first()
    region_name = region_info[0] if region_info else None
    birth_date = user.birthday
    current_date = datetime.now()
    age = current_date.year - birth_date.year
    if current_date.month < birth_date.month or \
        (current_date.month == birth_date.month and current_date.day < birth_date.day):
            age -= 1

    birthday = birth_date.strftime("%d.%m.%Y")
    user_info = {
        'email': user.email,
        'userName': user.name,
        'birthday': birthday,
        'age': age,
        'region': region_name,
        'Avatar': user.Avatar,
        'PublicLibrary': user.PublicLibrary,
        'LibraryType': user.LibraryType,
    }
    last_added_book = User.get_last_added_book(User, current_user_id=elseUserID)
    if last_added_book == None:
        return jsonify({'error': 'No book found for the specified conditions'}), 404
    readings=[]
    for book in last_added_book:
        reading={}
        reading = {
            'update_date':book.update_date,
            'book_title': book.Book_Title,
            'book_author': book.Book_Author,
            'image_url': book.Image_URL_M,
            'ISBN': book.ISBN
        } 
        reading['update_date'] = reading['update_date'].strftime("%d %B, %Y")
        readings.append(reading)
    shelves = User.get_shelves_covers(User, current_user_id=elseUserID)


    accountInfo = {
        'user_info': user_info,
        'currentlyReading': readings,
        'shelves': shelves
    }
    return jsonify(accountInfo), 200

@api_blueprint.route('/search/<string:searchPar>', methods=['GET'])
@cross_origin(origin='localhost', headers=['Content-Type'])
@jwt_required()
def search(searchPar):
    current_user_id = get_jwt_identity()
    books = Book.searchBooks(searchPar)
    booksWithUsers = User.bookOwners(User, books=books, userID=current_user_id)
    return jsonify(booksWithUsers)

@api_blueprint.route('/shelves/<int:userID>', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def getShelvesInfo(userID):
    verify_jwt_in_request()
    current_user_id = get_jwt_identity()
    if current_user_id != userID:
        return jsonify({'message': 'Unauthorized'}), 401

    shelves_with_books = User.get_shelves_with_books(User, userID)
    return jsonify(shelves_with_books), 200

@api_blueprint.route('/logout', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200

@api_blueprint.route('/book/<string:ISBN>', methods=['GET'])
@cross_origin(origin='localhost', headers=['Content- Type'])
@jwt_required()
def getBookInformation(ISBN):
    current_user_id = get_jwt_identity()

    bookInfo = User.get_shelves_and_book_info(User, user_id=current_user_id, isbn=ISBN)
    return jsonify(bookInfo), 200

@api_blueprint.route('/addBook', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def add_book_to_owned_books():
    data = request.get_json()
    ISBN = data.get('ISBN')
    current_user_id = get_jwt_identity()
    shelf_name = data.get('shelf_name')
    shelf_id = Shelf.get_shelf_id_by_name(shelf_name)
    current_date = datetime.now()
    CURRENTLY_READING_SHELF_ID = 5
    READ_SHELF_ID = 1

    if not ISBN or not shelf_name:
        return jsonify({'error': 'ISBN and shelf_name are required'}), 400

    insert_statement = db.text(
        """
        INSERT INTO OwnedBooks (ISBN, status_id, userID, update_date)
        VALUES (:isbn, :shelf_id, :user_id, :update_date)
        """
    )
    delete_statement = text(
        """
        DELETE FROM OwnedBooks
        WHERE ISBN = :isbn AND status_id = :currently_reading_shelf_id AND userID = :user_id
        """
    )
    select_statement = text(
        """
        SELECT 1 FROM OwnedBooks
        WHERE ISBN = :isbn AND status_id = :shelf_id AND userID = :user_id
        """
    )

    try:
        print(shelf_id)
        print(ISBN)
        # Check if the row already exists
        result = db.session.execute(
            select_statement,
            {'isbn': ISBN, 'shelf_id': shelf_id, 'user_id': current_user_id}
        ).fetchone()
        print(result)
        if result is None:
            # If the book is moved from "currently reading" to "read"
            if shelf_id == READ_SHELF_ID:
                db.session.execute(
                    delete_statement,
                    {'isbn': ISBN, 'currently_reading_shelf_id': CURRENTLY_READING_SHELF_ID, 'user_id': current_user_id}
                )
            
            # Insert the new row
            db.session.execute(
                insert_statement,
                {'isbn': ISBN, 'shelf_id': shelf_id, 'user_id': current_user_id, 'update_date': current_date}
            )
            db.session.commit()
            return jsonify({'message': 'Book added to OwnedBooks successfully'}), 201
        else:
            # Do nothing if the row already exists
            return jsonify({'message': 'Book already exists in OwnedBooks'}), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/update_rating', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def update_rating():
    data = request.json
    user_id = data.get('user_id')
    ISBN = data.get('ISBN')
    rating = data.get('rating')

    if user_id is None or ISBN is None or rating is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    try:
        select_statement = text(
            """
            SELECT ISBN
                ,userID
                ,status_id
                ,rating
                ,update_date
                ,secondUserID
                ,review
            FROM OwnedBooks
            WHERE userID = :user_id AND ISBN = :isbn AND status_id = 1
            ORDER BY update_date DESC
            """
        )
        result = db.session.execute(select_statement, {'user_id': user_id, 'isbn': ISBN}).fetchone()
        print(result[0])
        if result:
            update_statement = text(
                """
                UPDATE OwnedBooks
                SET rating = :rating
                WHERE userID = :user_id AND ISBN = :isbn AND status_id = 1 AND update_date = :update_date
                """
            )
            db.session.execute(update_statement, {'rating': rating, 'user_id': user_id, 'isbn': ISBN, 'update_date': result.update_date})
            db.session.commit()

            return jsonify({'message': 'Rating updated successfully'}), 200
        else:
            return jsonify({'error': 'No matching book found'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/getRating/<string:isbn>', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def get_rating(isbn):
    user_id = request.args.get('user_id')
    print("here")

    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400

    try:
        # Query to get the rating for the specified ISBN and user_id where status_id is 1
        query = text(
            """
            SELECT rating FROM OwnedBooks
            WHERE userID = :user_id AND ISBN = :isbn AND status_id = 1
            ORDER BY update_date DESC
            """
        )

        result = db.session.execute(query, {'user_id': user_id, 'isbn': isbn}).fetchone()
        print(result)
        if result:
            rating = int(result[0]) if result[0] is not None else 0
            return jsonify({'rating': rating}), 200
        else:
            return jsonify({'error': 'No matching book found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@api_blueprint.route('/deleteBook', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def delete_book():
    data = request.json
    user_id = data.get('user_id')
    ISBN = data.get('ISBN')
    shelf = data.get('shelf_name')


    if user_id is None or ISBN is None or shelf is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    shelf_id = Shelf.get_shelf_id_by_name(shelf_name=shelf)
    try:
        select_statement = text(
            """
            SELECT ISBN
                ,userID
                ,status_id
                ,rating
                ,update_date
                ,secondUserID
                ,review
            FROM OwnedBooks
            WHERE userID = :user_id AND ISBN = :isbn AND status_id = :shelf_id
            ORDER BY update_date DESC
            """
        )
        result = db.session.execute(select_statement, {'user_id': user_id, 'isbn': ISBN, 'shelf_id': shelf_id}).fetchone()
        print(result[0])
        if result:
            delete_statement = text(
                """
                DELETE FROM OwnedBooks
                WHERE userID = :user_id AND ISBN = :isbn AND status_id = :shelf_id AND update_date = :update_date
                """
            )
            db.session.execute(delete_statement, {'shelf_id': shelf_id, 'user_id': user_id, 'isbn': ISBN, 'update_date': result.update_date})
            db.session.commit()

            return jsonify({'message': 'Book deleted successfully'}), 200
        else:
            return jsonify({'error': 'No matching book found'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/leave_review', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@jwt_required()
def leave_review():
    data = request.json
    user_id = data.get('user_id')
    ISBN = data.get('ISBN')
    review = data.get('comment')

    if user_id is None or ISBN is None or review is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    try:
        select_statement = text(
            """
            SELECT ISBN
                ,userID
                ,status_id
                ,rating
                ,update_date
                ,secondUserID
                ,review
            FROM OwnedBooks
            WHERE userID = :user_id AND ISBN = :isbn AND status_id = 1
            ORDER BY update_date DESC
            """
        )
        result = db.session.execute(select_statement, {'user_id': user_id, 'isbn': ISBN}).fetchone()
        print(result[0])
        if result:
            update_statement = text(
                """
                UPDATE OwnedBooks
                SET review = :review
                WHERE userID = :user_id AND ISBN = :isbn AND status_id = 1 AND update_date = :update_date
                """
            )
            db.session.execute(update_statement, {'review': review, 'user_id': user_id, 'isbn': ISBN, 'update_date': result.update_date})
            db.session.commit()

            review_response = {
                'review': review,
                'username': result.username,
                'date': result.update_date.strftime("%d %B, %Y")
            }

            return jsonify(review_response), 200
        else:
            return jsonify({'error': 'No matching book found'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
