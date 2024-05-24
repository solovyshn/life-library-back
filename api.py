import pandas as pd
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin  
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
from models import User, Region,  db, Book, Shelf
from recommendations_prediction import predict_recommendations

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
    # if recommendations.empty != True:
    #     recommendations_dict = recommendations.to_dict(orient='records')
    # else:
    #     recommendations_dict=None
    if recommendations is None:
        recommendations_dict=None
        # Додаткові дії, коли recommendations є None
    elif isinstance(recommendations, pd.DataFrame):
        recommendations_dict = recommendations.to_dict(orient='records')
        # Додаткові дії, коли recommendations є DataFrame
        print(recommendations.head())  # Наприклад, виведення перших рядків DataFrame
    else:
        print("Recommendations are neither None nor a DataFrame.")


    accountInfo = {
        'user_info': user_info,
        'currentlyReading': readings,
        'recommendations': recommendations_dict if recommendations_dict else None,
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

    if not ISBN or not shelf_name:
        return jsonify({'error': 'ISBN and shelf_name are required'}), 400

    insert_statement = db.text(
        """
        INSERT INTO OwnedBooks (ISBN, status_id, userID, update_date)
        VALUES (:isbn, :shelf_id, :user_id, :update_date)
        """
    )
    try:
        db.session.execute(
            insert_statement,
            {'isbn': ISBN, 'shelf_id': shelf_id, 'user_id': current_user_id, 'update_date': current_date}
        )
        db.session.commit()
        return jsonify({'message': 'Book added to OwnedBooks successfully'}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': str(e)}), 500
