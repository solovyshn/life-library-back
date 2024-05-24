from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager 
from models import db
from api import api_blueprint

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@localhost/LifeLibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'

jwt = JWTManager(app)
db.init_app(app)

cors = CORS(app)
cors = CORS(app, resources={
    r"/register": {"origins": "http://localhost:3000", "methods": ["POST"]},
    r"/login": {"origins": "http://localhost:3000", "methods": ["POST"]},
    r"/regions": {"origins": "http://localhost:3000", "methods": ["GET"]},
    r"/account/*": {"origins": "http://localhost:3000", "methods": ["POST"]},
    r"/shelves/*": {"origins": "http://localhost:3000", "methods":["GET"]},
    r"/search/*": {"origins": "http://localhost:3000", "methods": ["GET"]},
    r"/book/*": {"origins": "http://localhost:3000", "methods": ["GET"]},
    r"/addBook": {"origins": "http://localhost:3000", "methods": ["POST"]}
})

app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
