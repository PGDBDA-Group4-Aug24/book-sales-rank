# from flask import Flask, render_template, request
# from tensorflow.keras.models import load_model
# import pandas as pd
# import numpy as np
# import pickle
# import keras.losses
# import matplotlib.pyplot as plt
# import io
# import base64
# import json

# app = Flask(__name__)

# # Corrected file path for Windows
# model_path = "model/ann_model2-final.h5"
# # Register 'mse' as a loss function
# keras.losses.mse = keras.losses.MeanSquaredError()

# # Load the model
# model = load_model(model_path, custom_objects={'mse': keras.losses.mse})

# # Load encoders & scalers
# with open("model/feature_scaler11.pkl", "rb") as f:
#     feature_scaler = pickle.load(f)

# with open("model/title_encoding.pkl", "rb") as f:
#     title_encoding = pickle.load(f)

# with open("model/label_encodings.pkl", "rb") as f:
#     label_encodings = pickle.load(f)

# with open("model/day_mapping.pkl", "rb") as f:
#     day_mapping = pickle.load(f)

# with open("model/targetencoding.pkl", "rb") as f:
#     target_encoding = pickle.load(f)

# # Load dataset (Make sure your dataset has the necessary columns)
# df = pd.read_csv("final_Cleaned_details3.csv")
# # df = pd.read_csv("dataset/final-amazon-cleanedfile.csv")
# df = df.drop(columns=['asin', 'year', 'timestamp', 'hour'], errors='ignore')


# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/analysis")
# def analysis():
#     return render_template("analysis.html")


# @app.route("/predict", methods=["POST"])
# def predict():
#     # Get input values from form
#     day = int(request.form["day"])
#     date = int(request.form["date"])
#     month = int(request.form["month"])
#     genre = request.form["genre"]
#     group = request.form["group"]

#     print("-------------------------", day)

#     # Ensure the input is present in the encoding dictionary
#     if genre not in label_encodings["genre"]:
#         return "Error: Genre not found in label encodings"
#     if group not in label_encodings["Group"]:
#         return "Error: Group not found in label encodings"
#     print(day)
#     # def encode_day(day):
#     #     day_mapping = {
#     #         "Monday": 0, "Tuesday": 1, "Wednesday": 2,
#     #         "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
#     #     }

#     # day = day_mapping.get(day)
#     # print(day)
#     # if day is None:
#     #     raise ValueError("Invalid day name")

#     # Convert day, date, and month to sine and cosine encoding
#     day_sin = np.sin(2 * np.pi * day / 7)
#     day_cos = np.cos(2 * np.pi * day / 7)
#     date_sin = np.sin(2 * np.pi * date / 31)
#     date_cos = np.cos(2 * np.pi * date / 31)
#     month_sin = np.sin(2 * np.pi * month / 12)
#     month_cos = np.cos(2 * np.pi * month / 12)

#     # Label Encode 'genre' and 'Group'
#     genre_encoded = label_encodings["genre"][genre]
#     group_encoded = label_encodings["Group"][group]

#     # Select a sample book dataset matching the genre and group
#     df_filtered = df[(df["genre"] == genre) & (df["Group"] == group)]

#     if df_filtered.empty:
#         return render_template("results.html", books=[])

#     # Apply Target Encoding for 'Author' and 'Publisher'
#     for col in ["Author", "publisher"]:
#         if col in target_encoding:
#             df_filtered[col] = df_filtered[col].map(target_encoding[col])

#     # Label Encode 'Format' and 'Title'
#     df_filtered["Format"] = df_filtered["Format"].map(
#         label_encodings["Format"])
#     df_filtered["Title"] = df_filtered["Title"].map(title_encoding)

#     # Ensure the selected features match the trained model's input
#     feature_columns = ["month_sin", "month_cos", "date_sin", "date_cos", "day_sin", "day_cos",
#                        "genre_encoded", "Group_encoded", "Format_encoded", "Author_encoded",
#                        "publisher_encoded"]

#     # Prepare DataFrame for prediction
#     df_filtered["month_sin"] = month_sin
#     df_filtered["month_cos"] = month_cos
#     df_filtered["date_sin"] = date_sin
#     df_filtered["date_cos"] = date_cos
#     df_filtered["day_sin"] = day_sin
#     df_filtered["day_cos"] = day_cos
#     df_filtered["genre_encoded"] = genre_encoded
#     df_filtered["Group_encoded"] = group_encoded

#     df_filtered["Format_encoded"] = df_filtered["Format"].map(
#         label_encodings["Format"]).fillna(-1)
#     df_filtered["title_encoded"] = df_filtered["Title"].map(
#         title_encoding).fillna(-1)
#     df_filtered["Author_encoded"] = df_filtered["Author"].map(
#         target_encoding["Author"]).fillna(-1)
#     df_filtered["publisher_encoded"] = df_filtered["publisher"].map(
#         target_encoding["Publisher"]).fillna(-1)

#     df_filtered["title_copy"] = df["Title"].copy()  # Copy the 'Title' column
#     df_filtered = df_filtered.drop(columns=[
#                                    'month', 'date', 'day', 'genre', 'Title', 'Author', 'Group', 'Format', 'publisher'])
#     df_filtered = df_filtered.drop(columns=['Unnamed: 0'])

#     feature_input = [col for col in df_filtered.columns if col not in [
#         "title_encoded", "rank", "title_copy"]]

#     # Check data types of all columns
#     print(df_filtered.dtypes)

#     # 1️⃣ Separate numerical and categorical (title) inputs
#     # Numerical features (scaled)
#     X_input_num = df_filtered[feature_input].values
#     # Title (for embedding)
#     X_input_title = df_filtered["title_encoded"].values

#     # 2️⃣ Apply MinMaxScaler to only numerical features
#     X_scaled = feature_scaler.transform(X_input_num)

#     # 3️⃣ Ensure title_encoded is reshaped correctly (for embedding input)
#     X_input_title = X_input_title.reshape(-1, 1)  # Reshape for embedding layer

#     # 4️⃣ Predict using both inputs
#     predictions = model.predict([X_scaled, X_input_title])
#     print(predictions)

#     # Inverse transform the target variable
#     df_filtered["Predicted Rank"] = predictions

#     # Convert to integers to remove scientific notation
#     df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].astype(int)
#     df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].abs()

#     print(df_filtered["Predicted Rank"])
#     print(df_filtered.columns)  # Ensure 'title_copy' exists
#     # Check data before sorting
#     print(df_filtered[["title_copy", "Predicted Rank"]].head(10))

#     # Check unique count for Predicted Rank
#     unique_rank_count = df_filtered["Predicted Rank"].nunique()

#     print(f"Unique Predicted Rank Count: {unique_rank_count}")

#     # Select unique books and sort by Predicted Rank
#     top_books = df_filtered[["title_copy", "Predicted Rank"]].drop_duplicates(
#         subset="title_copy").sort_values(by="Predicted Rank").head(10)
#     global_top_books=top_books
#     print(global_top_books)  # Check final output


#     # Pass top_books to template
#     return render_template("results.html", top_books=top_books)




# if __name__ == "__main__":
#     app.run(debug=True)

# # @app.route("/plot_trends", methods=["POST"])
# # def plot_trends():
# #     # Retrieve top_books from the form data (sent as a JSON string)
# #     # top_books_list = request.form.get("top_books")

# #     # # Convert the JSON string back into a Python list
# #     # top_books_list = json.loads(top_books_list)
# #     top_books_json = request.form.get("top_books")
    
# #     # Deserialize the JSON data back into a DataFrame
# #     top_books_df = pd.read_json(top_books_json)

# #     # Now you can proceed with filtering df and plotting trends
# #     print("Top books used in trend plotting:", top_books_df)

# #     if not top_books_df:
# #         return "Error: No books found for trends."

# #     # Filter the original dataframe 'df' to get the matching books for plotting
# #     trend_data = df[df["Title"].isin(top_books_df)]

# #     # Extract relevant trends: month, date, day
# #     trend_by_month = trend_data["month"].value_counts().sort_index()
# #     trend_by_day = trend_data["day"].value_counts().sort_index()
# #     trend_by_date = trend_data["date"].value_counts().sort_index()

# #     # Function to generate the image data for each plot and return it as base64
# #     def create_base64_image(plt):
# #         buf = io.BytesIO()
# #         plt.savefig(buf, format="png")
# #         buf.seek(0)
# #         img_data = base64.b64encode(buf.read()).decode("utf-8")
# #         buf.close()
# #         return img_data

# #     # Create plot for Trend by Month
# #     plt.figure(figsize=(8, 6))
# #     trend_by_month.plot(kind='bar', color='skyblue')
# #     plt.title("Books per Month")
# #     plt.xlabel("Month")
# #     plt.ylabel("Number of Books")
# #     month_trend_img = create_base64_image(plt)
# #     plt.close()

# #     # Create plot for Trend by Day
# #     plt.figure(figsize=(8, 6))
# #     trend_by_day.plot(kind='bar', color='lightgreen')
# #     plt.title("Books per Day")
# #     plt.xlabel("Day of the Week")
# #     plt.ylabel("Number of Books")
# #     day_trend_img = create_base64_image(plt)
# #     plt.close()

# #     # Create plot for Trend by Date
# #     plt.figure(figsize=(8, 6))
# #     trend_by_date.plot(kind='line', marker='o', color='salmon')
# #     plt.title("Books per Date")
# #     plt.xlabel("Date")
# #     plt.ylabel("Number of Books")
# #     date_trend_img = create_base64_image(plt)
# #     plt.close()

# #     # Pass the base64 image data to the template along with top_books data
# #     return render_template("trends.html", top_books=top_books_df,
# #                            month_trend_img=month_trend_img,
# #                            day_trend_img=day_trend_img,
# #                            date_trend_img=date_trend_img)

# @app.route("/plot_trend", methods=["POST"])
# def plot_trends():
#     global global_top_books_df  # Access the global variable again

#     # Check if the DataFrame exists and is not empty
#     if global_top_books_df is None or global_top_books_df.empty:
#         return "Error: No books found for trends."

#     # Trend plotting logic goes here
#     # For example: 
#     trend_by_month = global_top_books_df['title_copy'].value_counts().sort_index()

#     # Create the trend plot and save it as base64 image for rendering
#     plt.figure(figsize=(8, 6))
#     trend_by_month.plot(kind='bar', color='skyblue')
#     plt.title("Books per Month")
#     plt.xlabel("Month")
#     plt.ylabel("Number of Books")

#     # Save the plot to a BytesIO object and encode it to base64
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     img_data = base64.b64encode(buf.read()).decode('utf-8')
#     buf.close()

#     # Render the plot in a template
#     return render_template('trends.html', month_trend_img=img_data)

from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import pickle
import keras.losses
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Corrected file path for Windows
model_path = "model/ann_model2-final.h5"
# Register 'mse' as a loss function
keras.losses.mse = keras.losses.MeanSquaredError()

# Load the model
model = load_model(model_path, custom_objects={'mse': keras.losses.mse})

# Load encoders & scalers
with open("model/feature_scaler11.pkl", "rb") as f:
    feature_scaler = pickle.load(f)

with open("model/title_encoding.pkl", "rb") as f:
    title_encoding = pickle.load(f)

with open("model/label_encodings.pkl", "rb") as f:
    label_encodings = pickle.load(f)

with open("model/day_mapping.pkl", "rb") as f:
    day_mapping = pickle.load(f)

with open("model/targetencoding.pkl", "rb") as f:
    target_encoding = pickle.load(f)

# Load dataset (Make sure your dataset has the necessary columns)
df = pd.read_csv("final_Cleaned_details3.csv")
df = df.drop(columns=['asin', 'year', 'timestamp', 'hour'], errors='ignore')

global_top_books_df = None  # Initialize a global variable to store the top books DataFrame


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

    print("-------------------------", day)

    # Ensure the input is present in the encoding dictionary
    if genre not in label_encodings["genre"]:
        return "Error: Genre not found in label encodings"
    if group not in label_encodings["Group"]:
        return "Error: Group not found in label encodings"
    
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

    df_filtered["Format_encoded"] = df_filtered["Format"].map(label_encodings["Format"]).fillna(-1)
    df_filtered["title_encoded"] = df_filtered["Title"].map(title_encoding).fillna(-1)
    df_filtered["Author_encoded"] = df_filtered["Author"].map(target_encoding["Author"]).fillna(-1)
    df_filtered["publisher_encoded"] = df_filtered["publisher"].map(target_encoding["Publisher"]).fillna(-1)

    df_filtered["title_copy"] = df["Title"].copy()  # Copy the 'Title' column
    df_filtered = df_filtered.drop(columns=['month', 'date', 'day', 'genre', 'Title', 'Author', 'Group', 'Format', 'publisher'])
    df_filtered = df_filtered.drop(columns=['Unnamed: 0'])

    feature_input = [col for col in df_filtered.columns if col not in ["title_encoded", "rank", "title_copy"]]

    # Separate numerical and categorical (title) inputs
    X_input_num = df_filtered[feature_input].values
    X_input_title = df_filtered["title_encoded"].values

    # Apply MinMaxScaler to only numerical features
    X_scaled = feature_scaler.transform(X_input_num)

    # Ensure title_encoded is reshaped correctly (for embedding input)
    X_input_title = X_input_title.reshape(-1, 1)

    # Predict using both inputs
    predictions = model.predict([X_scaled, X_input_title])

    # Inverse transform the target variable
    df_filtered["Predicted Rank"] = predictions
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].astype(int)
    df_filtered["Predicted Rank"] = df_filtered["Predicted Rank"].abs()

    # Store the top books for trend plotting
    global global_top_books_df
    global_top_books_df = df_filtered[["title_copy", "Predicted Rank"]].drop_duplicates(subset="title_copy").sort_values(by="Predicted Rank").head(10)

    return render_template("results.html", top_books=global_top_books_df)


# @app.route("/plot_trend", methods=["GET", "POST"])  # Allow both GET and POST methods
# def plot_trends():
#     global global_top_books_df  # Access the global variable containing top books
#     global df  # Access the global DataFrame containing the full dataset

#     # Check if global_top_books_df exists and is not empty
#     if global_top_books_df is None or global_top_books_df.empty:
#         return "Error: No books found for trends."

#     # Check if df exists and is not empty
#     if df is None or df.empty:
#         return "Error: No data available to plot trends."

#     # Extract titles from global_top_books_df
#     top_titles = global_top_books_df['title_copy'].tolist()  # 'title_copy' used in top_books_df

#     # Filter the main df for rows where the Title is in top_titles
#     filtered_df = df[df['Title'].isin(top_titles)]  # 'Title' is the column in the main df

#     # Check if filtered_df has data
#     if filtered_df.empty:
#         return "Error: No matching titles found in the dataset for trend plotting."

#     # Create multiple trend plots for each title
#     plots = []
#     for title in top_titles:
#         book_data = filtered_df[filtered_df['Title'] == title]

#         if book_data.empty:
#             continue  # Skip this title if no data is found in the main df

#         # Group by month and day for trend plotting
#         trend_by_month = book_data.groupby('month')['rank'].mean()
#         trend_by_day = book_data.groupby('day')['rank'].mean()

#         # Create the month trend plot
#         plt.figure(figsize=(8, 6))
#         trend_by_month.plot(kind='bar', color='skyblue')
#         plt.title(f"Monthly Rank Trend for {title}")
#         plt.xlabel("Month")
#         plt.ylabel("Average Rank")

#         # Save the monthly plot to a BytesIO object
#         buf_month = io.BytesIO()
#         plt.savefig(buf_month, format='png')
#         buf_month.seek(0)
#         month_img_data = base64.b64encode(buf_month.read()).decode('utf-8')
#         buf_month.close()

#         # Create the day trend plot
#         plt.figure(figsize=(8, 6))
#         trend_by_day.plot(kind='bar', color='lightgreen')
#         plt.title(f"Daily Rank Trend for {title}")
#         plt.xlabel("Day")
#         plt.ylabel("Average Rank")

#         # Save the daily plot to a BytesIO object
#         buf_day = io.BytesIO()
#         plt.savefig(buf_day, format='png')
#         buf_day.seek(0)
#         day_img_data = base64.b64encode(buf_day.read()).decode('utf-8')
#         buf_day.close()

#         # Append the images to the list of plots for rendering
#         plots.append({
#             'title': title,
#             'month_trend_img': month_img_data,
#             'day_trend_img': day_img_data
#         })

#     # Render the plots in a template
#     return render_template('trends.html', plots=plots)
@app.route("/plot_trend", methods=["GET", "POST"])  # Allow both GET and POST methods
def plot_trends():
    global global_top_books_df  # Access the global variable containing top books
    global df  # Access the global DataFrame containing the full dataset

    # Check if global_top_books_df exists and is not empty
    if global_top_books_df is None or global_top_books_df.empty:
        return "Error: No books found for trends."

    # Check if df exists and is not empty
    if df is None or df.empty:
        return "Error: No data available to plot trends."

    # Extract titles from global_top_books_df
    top_titles = global_top_books_df['title_copy'].tolist()  # 'title_copy' used in top_books_df

    # Filter the main df for rows where the Title is in top_titles
    filtered_df = df[df['Title'].isin(top_titles)]  # 'Title' is the column in the main df

    # Check if filtered_df has data
    if filtered_df.empty:
        return "Error: No matching titles found in the dataset for trend plotting."

    # Create multiple trend plots for each title
    plots = []
    for title in top_titles:
        book_data = filtered_df[filtered_df['Title'] == title]

        if book_data.empty:
            continue  # Skip this title if no data is found in the main df

        # Group by month and day for trend plotting
        trend_by_month = book_data.groupby('month')['rank'].mean()
        trend_by_day = book_data.groupby('day')['rank'].mean()

        # Create the month trend line plot
        plt.figure(figsize=(8, 6))
        trend_by_month.plot(kind='line', marker='o', linestyle='-', color='skyblue')
        plt.title(f"Monthly Rank Trend for {title}")
        plt.xlabel("Month")
        plt.ylabel("Average Rank")
        plt.grid(True)

        # Save the monthly plot to a BytesIO object
        buf_month = io.BytesIO()
        plt.savefig(buf_month, format='png')
        buf_month.seek(0)
        month_img_data = base64.b64encode(buf_month.read()).decode('utf-8')
        buf_month.close()

        # Create the day trend line plot
        plt.figure(figsize=(8, 6))
        trend_by_day.plot(kind='line', marker='o', linestyle='-', color='lightgreen')
        plt.title(f"Daily Rank Trend for {title}")
        plt.xlabel("Day")
        plt.ylabel("Average Rank")
        plt.grid(True)

        # Save the daily plot to a BytesIO object
        buf_day = io.BytesIO()
        plt.savefig(buf_day, format='png')
        buf_day.seek(0)
        day_img_data = base64.b64encode(buf_day.read()).decode('utf-8')
        buf_day.close()

        # Append the images to the list of plots for rendering
        plots.append({
            'title': title,
            'month_trend_img': month_img_data,
            'day_trend_img': day_img_data
        })

    # Render the plots in a template
    return render_template('trends.html', plots=plots)


if __name__ == "__main__":
    app.run(debug=True)