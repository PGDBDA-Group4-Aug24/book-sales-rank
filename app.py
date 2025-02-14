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


# Corrected file path for Windows
model_path = "model/ann_model--final.h5"
# Register 'mse' as a loss function
keras.losses.mse = keras.losses.MeanSquaredError()

# Load the model
model = load_model(model_path, custom_objects={'mse': keras.losses.mse})

# Load encoders & scalers
with open("model/feature_scaler.pkl", "rb") as f:
    feature_scaler = pickle.load(f)

with open("model/title_encoding.pkl", "rb") as f:
    title_encoding = pickle.load(f)

with open("model/author_encoding.pkl", "rb") as f:
    author_encodings = pickle.load(f)

with open("model/format_encoding.pkl", "rb") as f:
    format_encoding = pickle.load(f)

with open("model/genre_encoding.pkl", "rb") as f:
    genre_encoding = pickle.load(f)
    
with open("model/group_encoding.pkl", "rb") as f:
    group_encoding = pickle.load(f)

with open("model/publisher_encoding.pkl", "rb") as f:
    publisher_encoding = pickle.load(f)


with open("model/day_mapping.pkl", "rb") as f:
    day_mapping = pickle.load(f)
    
# Load dataset (Make sure your dataset has the necessary columns)
df = pd.read_csv("unique_data.csv",on_bad_lines="skip")

 
# Initialize a global variable to store the top books DataFrame
global_top_books_df = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Get input values from form
    day = int(request.form["day"])
    date = int(request.form["date"])
    month = int(request.form["month"])
    genre = request.form["genre"]
    group = request.form["group"]

    
    if genre not in genre_encoding:
        return "Error: Genre not found in label encodings"
    if group not in group_encoding:
        return "Error: Group not found in label encodings"

    # Convert day, date, and month to sine and cosine encoding
    day_sin = np.sin(2 * np.pi * day / 7)
    day_cos = np.cos(2 * np.pi * day / 7)
    date_sin = np.sin(2 * np.pi * date / 31)
    date_cos = np.cos(2 * np.pi * date / 31)
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)

    # Label Encode 'genre' and 'Group'
    genre_encoded = genre_encoding[genre]
    group_encoded = group_encoding[group]

    # Select a sample book dataset matching the genre and group
    df_filtered = df[(df["GENRE"] == genre) & (df["GROUP"] == group)]

    if df_filtered.empty:
        return render_template("results.html", books=[])

    # map the authors and publishers using the loaded encodings
    df_filtered["Author_encoded"] = df_filtered["AUTHOR"].map(author_encodings)
    df_filtered["Publisher_encoded"] = df_filtered["PUBLISHER"].map(publisher_encoding)

    # Label Encode 'Format' and 'Title'
    df_filtered["Format"] = df_filtered["FORMAT"].map(format_encoding)
    df_filtered["Title"] = df_filtered["TITLE"].map(title_encoding)

    # Ensure the selected features match the trained model's input
    feature_columns = ["month_sin", "month_cos", "date_sin", "date_cos", "day_sin", "day_cos",
                       "genre_encoded", "Group_encoded", "Format_encoded", "Author_encoded", "publisher_encoded"]

    # Prepare DataFrame for prediction
    df_filtered["month_sin"] = month_sin
    df_filtered["month_cos"] = month_cos
    df_filtered["date_sin"] = date_sin
    df_filtered["date_cos"] = date_cos
    df_filtered["day_sin"] = day_sin
    df_filtered["day_cos"] = day_cos
    df_filtered["genre_encoded"] = genre_encoded
    df_filtered["Group_encoded"] = group_encoded

    df_filtered["Format_encoded"] = df_filtered["FORMAT"].map(
        format_encoding).fillna(-1)
    df_filtered["title_encoded"] = df_filtered["TITLE"].map(
        title_encoding).fillna(-1)
    df_filtered["Author_encoded"] = df_filtered["AUTHOR"].map(
        author_encodings).fillna(-1)
    df_filtered["publisher_encoded"] = df_filtered["PUBLISHER"].map(
        publisher_encoding).fillna(-1)

    df_filtered["title_copy"] = df["TITLE"].copy()  # Copy the 'Title' column

    print(df_filtered.columns)

    df_filtered = df_filtered.drop(columns=[ 'GENRE', 'TITLE', 'AUTHOR', 'GROUP', 'FORMAT', 'PUBLISHER'])
    
    #model setup

    feature_input = [col for col in df_filtered.columns if col not in [
        "title_encoded", "rank", "title_copy"]]
    numeric_features = ['month_sin', 'month_cos', 'date_sin', 'date_cos', 'day_sin', 'day_cos']

    numeric_features = np.array([[month_sin, month_cos, date_sin, date_cos, day_sin, day_cos]])
    # categorical_features = np.array([[author_encodings, publisher_encoding, genre_encoded, group_encoded, format_encoding, title_encoding]])
    

    # Reshape categorical inputs for embeddings
    # Convert categorical features into numpy arrays and reshape
    X_input_author = np.array(df_filtered["Author_encoded"].values)  # Shape: (n_samples, 1)
    X_input_publisher = np.array(df_filtered["Publisher_encoded"].values)
    X_input_genre = np.array(df_filtered["genre_encoded"].values)
    X_input_group = np.array(df_filtered["Group_encoded"].values)
    X_input_format = np.array(df_filtered["Format_encoded"].values)
    X_input_title = np.array(df_filtered["title_encoded"].values)
    print(X_input_author.shape)

    # Normalize the numeric features
    numeric_features = feature_scaler.transform(numeric_features)
    X_scaled = np.tile(numeric_features, (df_filtered.shape[0], 1))
    
    # Reshape categorical inputs for embedding layers
    X_input_author = X_input_author.reshape(-1, 1)
    X_input_publisher = X_input_publisher.reshape(-1, 1)
    X_input_genre = X_input_genre.reshape(-1, 1)
    X_input_group = X_input_group.reshape(-1, 1)
    X_input_format = X_input_format.reshape(-1, 1)
    X_input_title = X_input_title.reshape(-1, 1)

    max_publisher_encoded = df_filtered["Publisher_encoded"].max()
    print(f"Maximum value in Publisher_encoded: {max_publisher_encoded}")

    # Predict using both numerical and categorical inputs
    predictions = model.predict([X_scaled, X_input_author, X_input_publisher, X_input_genre, X_input_group, X_input_format, X_input_title]).flatten()[0]

    # Inverse transform the target variable
    # Process predictions
    df_filtered["Predicted Rank"] = predictions
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].astype(int)
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].abs()

    # Store the top books for trend plotting
    global global_top_books_df
    
    global_top_books_df = df_filtered[["title_copy", "Predicted Rank"]].drop_duplicates(
        subset="title_copy").sort_values(by="Predicted Rank").head(10)
    
    return render_template("results.html", top_books=global_top_books_df)

#----------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)