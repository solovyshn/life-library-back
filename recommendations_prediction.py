import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from models import Book, db, User
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

def predict_books_liked(model, label_encoder, df, genre_mapping):
    predictions = []
    for index, row in df.iterrows():
        genre_encoded = genre_mapping.get(row['Genre'])
        features = [[row['Average_rating'], row['Ratings_count'], row['Year_Of_Publisher'], genre_encoded]]
        prediction = model.predict(features)
        predictions.append(prediction[0])
    
    df['predicted_liked'] = predictions
    liked_books_predictions = df[df['predicted_liked'] == 1]
    return liked_books_predictions

def train_and_tune_model(X_train, y_train):
    param_grid = {
        'learning_rate': [0.05, 0.1, 0.2],
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7]
    }
    gb_clf = GradientBoostingClassifier(learning_rate=1.0, max_depth=1, random_state=42)
    grid_search = GridSearchCV(estimator=gb_clf, param_grid=param_grid, cv=4, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_


def predict_recommendations(userID):
    label_encoder = LabelEncoder()

    books_data = Book.get_all_books(Book, db.session)
    booksDF = pd.DataFrame(books_data)
    booksDF['genre_encoded'] = label_encoder.fit_transform(booksDF['Genre'])
    genre_mapping = booksDF.set_index('Genre')['genre_encoded'].to_dict()

    user_ratings = User.get_book_ratings(User, db.session, userID)
    if len(user_ratings) < 5:
        return None
    combined_data = []
    for user_rating in user_ratings:
        book_info = next((book for book in books_data if book['ISBN'] == user_rating['ISBN']), None)
        if book_info:
            combined_info = {
                'ISBN': user_rating['ISBN'],
                'rating': user_rating['rating'],
                'Year_Of_Publisher': book_info['Year_Of_Publisher'],
                'Genre': book_info['Genre'],
                'Average_rating': book_info['Average_rating'],
                'Ratings_count': book_info['Ratings_count']
            }
            combined_data.append(combined_info)
    df = pd.DataFrame(combined_data)

    isbns_to_remove = df['ISBN']
    booksDF = booksDF[~booksDF['ISBN'].isin(isbns_to_remove)]

    threshold = 4.0
    conditions = [
        df['rating'] >= threshold,
        df['rating'] < threshold,
    ]
    choices = [1, 0]
    df['liked'] = np.select(conditions, choices)
    df['genres_encoded'] = df['Genre'].map(genre_mapping)

    X = df[['Average_rating', 'Ratings_count', 'Year_Of_Publisher', 'genres_encoded']]
    y = df['liked']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    best_model = train_and_tune_model(X_train, y_train)
    predictions = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    predicted = predict_books_liked(model=best_model, label_encoder=label_encoder, df=booksDF, genre_mapping=genre_mapping)
    print(f"Accuracy: {accuracy}")
    return predicted[['ISBN', 'Image_URL_M', 'Book_Title', 'Book_Author']]
