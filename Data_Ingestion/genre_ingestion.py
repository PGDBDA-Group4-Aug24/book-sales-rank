import os
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# 🔹 Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")

# 🔹 Load a *local, fast* model (No Hugging Face token required)
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)

# 🔹 Load book titles from CSV
csv_file = '/content/hemant-file.csv'  # Update with your actual file path
df = pd.read_csv(csv_file)

# 🔹 Check if 'TITLE' column exists
if "TITLE" not in df.columns:
    raise ValueError("CSV file must contain a 'TITLE' column.")

# 🔹 Define possible genres
genres = ["fiction", "mystery", "fantasy", "science fiction", "romance", "history", "biography", "horror"]

# 🔹 Encode genres *once* for fast lookup
genre_embeddings = model.encode(genres, convert_to_tensor=True)

# 🔹 Predict genres using *Cosine Similarity*
predicted_genres = []
for title in tqdm(df["TITLE"], desc="Processing Titles", unit="book"):
    title_embedding = model.encode([title], convert_to_tensor=True)  # Encode title
    similarities = cosine_similarity(title_embedding.cpu(), genre_embeddings.cpu())  # Compare with genres
    best_match = genres[similarities.argmax()]  # Find best-matching genre
    predicted_genres.append(best_match)

# 🔹 Save results to a new CSV file
df["predicted_genre"] = predicted_genres
output_file = "books_with_genres.csv"
df.to_csv(output_file, index=False)

print(f"✅ Predictions saved to {output_file}")