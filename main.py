# from sqlalchemy import create_engine
# import SQLAlchemy
# from sqlalchemy.orm import sessionmaker
# from models import Base, Book, User
# from flask import Flask, request, jsonify
# from models import User
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import User, db
from flask_cors import CORS, cross_origin    # Import Flask-CORS

# # Create an engine and bind the session
# engine = create_engine('mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
# Session = sessionmaker(bind=engine)
# session = Session()

# # Query the database using the generated classes
# result = session.query(Book).filter(Book.Year_Of_Publication == 2003).all()
# print(result)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'

db.init_app(app)
cors = CORS(app, resources={r"/register": {'origins': 'http://localhost:3000'}})

@app.route('/register', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def register():
    data = request.get_json()

    if 'yourName' not in data or 'yourEmail' not in data or 'yourPassword' not in data or 'region' not in data or 'birthday' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    if User.email_exists(data['yourEmail']):
        return jsonify({'error': 'Email already exists'}), 409  # 409 for conflict
    last_id = User.get_last_id(User)
    if last_id is None:
        userID = 1
    else:
        userID = last_id+1

    new_user = User(Name=data['yourName'], Email=data['yourEmail'], Password=data['yourPassword'], Birthday=data['birthday'], Region=data['region'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def login():
    data = request.get_json()
    if 'yourEmail' not in data or 'yourPassword' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    email = data['yourEmail']
    password = data['yourPassword']
    user = User.query.filter_by(Email=email).first()
    if user:
        # Verify the password
        if user.Password == password:
            return jsonify({'message': 'User logged in successfully'}), 200
        else:
            return jsonify({'error': 'Incorrect password'}), 401
    else:
        return jsonify({'error': 'User with this email doesn\'t exist'}), 404

if __name__ == '__main__':
    app.run(debug=True)
