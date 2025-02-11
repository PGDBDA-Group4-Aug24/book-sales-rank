from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import pickle
import keras.losses


app = Flask(__name__)

# Corrected file path for Windows
model_path = "ann-model2/model/ann_model2-final.h5"
# Register 'mse' as a loss function
keras.losses.mse = keras.losses.MeanSquaredError()

# Load the model
model = load_model(model_path, custom_objects={'mse': keras.losses.mse})

# Load encoders & scalers
with open("ann-model2/model/feature_scaler11.pkl", "rb") as f:
    feature_scaler = pickle.load(f)

with open("ann-model2/model/title_encoding.pkl", "rb") as f:
    title_encoding = pickle.load(f)

with open("ann-model2/model/label_encodings.pkl", "rb") as f:
    label_encodings = pickle.load(f)

with open("ann-model2/model/day_mapping.pkl", "rb") as f:
    day_mapping = pickle.load(f)

with open("ann-model2/model/targetencoding.pkl", "rb") as f:
    target_encoding = pickle.load(f)

# Load dataset (Make sure your dataset has the necessary columns)
df = pd.read_csv("dataset/final_Cleaned_details3.csv")
#df = pd.read_csv("dataset/final-amazon-cleanedfile.csv")
df = df.drop(columns=['asin', 'year', 'timestamp', 'hour'], errors='ignore')


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Get input values from form
    day = int(request.form["day"])
    date = int(request.form["date"])
    month = int(request.form["month"])
    genre = request.form["genre"]
    group = request.form["group"]
    
    print("-------------------------",day)

    # Ensure the input is present in the encoding dictionary
    if genre not in label_encodings["genre"]:
        return "Error: Genre not found in label encodings"
    if group not in label_encodings["Group"]:
        return "Error: Group not found in label encodings"
    print(day)
    # def encode_day(day):
    #     day_mapping = {
    #         "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    #         "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
    #     }
    
    # day = day_mapping.get(day)
    # print(day)
    # if day is None:
    #     raise ValueError("Invalid day name")

    # Convert day, date, and month to sine and cosine encoding
    day_sin = np.sin(2 * np.pi * day / 7)
    day_cos = np.cos(2 * np.pi * day / 7)
    date_sin = np.sin(2 * np.pi * date / 31)
    date_cos = np.cos(2 * np.pi * date / 31)
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)

    # Label Encode 'genre' and 'Group'
    genre_encoded = label_encodings["genre"][genre]
    group_encoded = label_encodings["Group"][group]

    # Select a sample book dataset matching the genre and group
    df_filtered = df[(df["genre"] == genre) & (df["Group"] == group)]

    if df_filtered.empty:
        return render_template("results.html", books=[])

    # Apply Target Encoding for 'Author' and 'Publisher'
    for col in ["Author", "publisher"]:
        if col in target_encoding:
            df_filtered[col] = df_filtered[col].map(target_encoding[col])

    # Label Encode 'Format' and 'Title'
    df_filtered["Format"] = df_filtered["Format"].map(label_encodings["Format"])
    df_filtered["Title"] = df_filtered["Title"].map(title_encoding)

    # Ensure the selected features match the trained model's input
    feature_columns = ["month_sin", "month_cos", "date_sin", "date_cos", "day_sin", "day_cos",
                       "genre_encoded", "Group_encoded", "Format_encoded", "Author_encoded",
                       "publisher_encoded"]

    # Prepare DataFrame for prediction
    df_filtered["month_sin"] = month_sin
    df_filtered["month_cos"] = month_cos
    df_filtered["date_sin"] = date_sin
    df_filtered["date_cos"] = date_cos
    df_filtered["day_sin"] = day_sin
    df_filtered["day_cos"] = day_cos
    df_filtered["genre_encoded"] = genre_encoded
    df_filtered["Group_encoded"] = group_encoded

    df_filtered["Format_encoded"] = df_filtered["Format"].map(label_encodings["Format"]).fillna(-1)
    df_filtered["title_encoded"] = df_filtered["Title"].map(title_encoding).fillna(-1)
    df_filtered["Author_encoded"] = df_filtered["Author"].map(target_encoding["Author"]).fillna(-1) 
    df_filtered["publisher_encoded"] = df_filtered["publisher"].map(target_encoding["Publisher"]).fillna(-1)
    
    df_filtered["title_copy"] = df["Title"].copy()  # Copy the 'Title' column
    df_filtered = df_filtered.drop(columns=[ 'month', 'date', 'day', 'genre', 'Title', 'Author', 'Group', 'Format', 'publisher']) 
    df_filtered = df_filtered.drop(columns=['Unnamed: 0'])

    feature_input = [col for col in df_filtered.columns if col not in ["title_encoded", "rank","title_copy"]]

    
    # Check data types of all columns
    print(df_filtered.dtypes)


    # 1️⃣ Separate numerical and categorical (title) inputs
    X_input_num = df_filtered[feature_input].values  # Numerical features (scaled)
    X_input_title = df_filtered["title_encoded"].values  # Title (for embedding)
    
   

    # 2️⃣ Apply MinMaxScaler to only numerical features
    X_scaled = feature_scaler.transform(X_input_num)

    # 3️⃣ Ensure title_encoded is reshaped correctly (for embedding input)
    X_input_title = X_input_title.reshape(-1, 1)  # Reshape for embedding layer

    # 4️⃣ Predict using both inputs
    predictions = model.predict([X_scaled, X_input_title])
    print(predictions)

    # Inverse transform the target variable
    df_filtered["Predicted Rank"] =predictions
    
    # Convert to integers to remove scientific notation
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].astype(int)
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].abs()


    print(df_filtered["Predicted Rank"])
    print(df_filtered.columns)  # Ensure 'title_copy' exists
    print(df_filtered[["title_copy", "Predicted Rank"]].head(10))  # Check data before sorting
    
    # Check unique count for Predicted Rank
    unique_rank_count = df_filtered["Predicted Rank"].nunique()

    print(f"Unique Predicted Rank Count: {unique_rank_count}")


    # Select unique books and sort by Predicted Rank
    top_books = df_filtered[["title_copy", "Predicted Rank"]].drop_duplicates(subset="title_copy").sort_values(by="Predicted Rank").head(10)

    print(top_books)  # Check final output

    
    # Pass top_books to template
    return render_template("results.html", top_books=top_books)

if __name__ == "__main__":
    app.run(debug=True)
