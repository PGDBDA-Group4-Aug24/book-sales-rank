from flask import Flask, render_template, request, redirect, url_for, session
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def predict_book_success(book_data):
    """
    Make predictions based on book data using a genre-based scoring system
    """
    try:
        # Get the genre and normalize the score based on genre popularity
        genre = book_data.get('genre', 'fiction').lower()
        genre_scores = {
            'fiction': 85,
            'non-fiction': 75,
            'mystery': 80,
            'sci-fi': 70,
            'romance': 82,
            'thriller': 78
        }

        base_score = genre_scores.get(genre, 70)

        # Adjust score based on page count
        pages = int(book_data.get('pages', 300))
        if 200 <= pages <= 400:
            page_adjustment = 5
        elif pages < 200:
            page_adjustment = -5
        else:
            page_adjustment = 0

        # Final score calculation
        success_rate = min(100, max(0, base_score + page_adjustment))

        return {
            'success_rate': success_rate,
            'genre_match': 'High' if success_rate > 75 else 'Medium' if success_rate > 60 else 'Low',
            'target_audience': 'Young Adults' if genre in ['sci-fi', 'romance'] else 'General Audience',
            'market_potential': 'Good' if success_rate > 70 else 'Fair' if success_rate > 50 else 'Limited'
        }

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            'success_rate': 50,
            'genre_match': 'Medium',
            'target_audience': 'General',
            'market_potential': 'Fair'
        }

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/prediction', methods=['GET'])
def prediction():
    return render_template('prediction.html')

@app.route('/prediction_result', methods=['POST'])
def prediction_result():
    if request.method == 'POST':
        book_data = {
            'title': request.form.get('title'),
            'author': request.form.get('author'),
            'genre': request.form.get('genre'),
            'pages': request.form.get('pages'),
            'description': request.form.get('description')
        }

        # Log the received data
        logger.debug(f"Received book data: {book_data}")

        # Get prediction results
        prediction_results = predict_book_success(book_data)
        logger.debug(f"Prediction results: {prediction_results}")

        # Store in session for analysis page
        session['book_data'] = book_data
        session['prediction_results'] = prediction_results

        return render_template('prediction_result.html',
                             book_data=book_data,
                             prediction=prediction_results)

@app.route('/analysis')
def analysis():
    # Retrieve data from session
    book_data = session.get('book_data', {})
    prediction_results = session.get('prediction_results', {})

    if not book_data or not prediction_results:
        return redirect(url_for('prediction'))

    return render_template('analysis.html',
                         book_data=book_data,
                         prediction=prediction_results)

if __name__ == '__main__':
    app.run(debug=True)