import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the file, skipping problematic lines
try:
    df = pd.read_csv("C://Users//shubh//Downloads//amazon_com_extras.csv//amazon_com_extras.csv", on_bad_lines="skip", encoding="ISO-8859-1")  # Adjust encoding if needed
    print("Dataset loaded successfully!")
except Exception as e:
    print(f"Error loading dataset: {e}")

# Save the cleaned dataset
cleaned_file = "cleaned_dataset.csv"
df.to_csv(cleaned_file, index=False)
print(f"Cleaned dataset saved to {cleaned_file}")

# Genre dictionary with related keywords in list format
genre_dict = {
    "Fiction": {
        "Literary Fiction": ["style", "character development", "thematic depth", "literary"],
        "Historical Fiction": ["history", "past", "real events", "fictional characters", "period"],
        "Mystery": ["crime", "investigation", "puzzle", "detective", "clue"],
        "Thriller": ["suspense", "excitement", "danger", "high stakes", "action-packed"],
        "Science Fiction": ["futuristic", "space", "technology", "time travel", "aliens", "robots"],
        "Fantasy": ["magic", "mythical creatures", "imaginary worlds", "supernatural", "epic"],
        "Adventure": ["action", "quest", "journey", "exploration", "risk"],
        "Romance": ["love", "relationship", "emotions", "romantic", "hugs", "kisses"],
        "Horror": ["fear", "supernatural", "creepy", "disturbing", "monsters", "darkness"],
        "Young Adult (YA)": ["teen", "coming-of-age", "growth", "adolescence", "relationships"],
        "Children’s Fiction": ["kids", "imagination", "fun", "innocence", "playful"],
        "Dystopian": ["post-apocalyptic", "totalitarian", "society", "rebellion", "future"],
        "Magical Realism": ["magic", "realism", "dreamlike", "surreal", "ordinary meets extraordinary"]
    },
    "Non-Fiction": {
        "Biography": ["life story", "person", "real events", "true account", "personal journey"],
        "Autobiography": ["self", "personal story", "first-person", "memoir", "life experience"],
        "Memoir": ["memory", "personal", "experiences", "specific events", "reflection"],
        "Self-Help": ["personal growth", "improvement", "motivation", "advice", "well-being"],
        "True Crime": ["real crime", "investigation", "criminal case", "murder", "justice"],
        "Travel": ["journey", "exploration", "places", "adventure", "destinations", "culture"],
        "Cookbook": ["recipes", "cooking", "food", "ingredients", "chef", "meal planning"],
        "Health & Wellness": ["fitness", "well-being", "nutrition", "mental health", "exercise"],
        "Psychology": ["mind", "behavior", "emotions", "cognition", "mental processes"],
        "Philosophy": ["existence", "ethics", "knowledge", "reality", "reasoning", "morality"],
        "History": ["past", "events", "timeline", "historical", "figures", "chronicle"],
        "Science": ["biology", "physics", "chemistry", "research", "discovery", "innovation"]
    }
}

# Flatten the genre dictionary and prepare a list of genre names and keywords
genre_keywords = []
genre_names = []

for genre_type, genres in genre_dict.items():
    for genre, keywords in genres.items():
        genre_keywords.append(" ".join(keywords))  # Join keywords for each genre into one string
        genre_names.append(genre)

# Initialize the TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')

# Vectorize the genre keywords (each genre becomes a vector)
genre_vectors = vectorizer.fit_transform(genre_keywords)

# Define a function to assign genre based on the TITLE using cosine similarity
def assign_genre(row):
    title = str(row.get('TITLE', '')).lower()  # Safely handle missing 'TITLE'
    
    # Vectorize the title
    title_vector = vectorizer.transform([title])
    
    # Compute cosine similarities between the title vector and all genre vectors
    similarities = cosine_similarity(title_vector, genre_vectors)
    
    # Find the index of the highest similarity score
    best_match_index = np.argmax(similarities)
    
    # Return the genre corresponding to the highest similarity
    return genre_names[best_match_index]

# Apply the function to create a new column for Genre
if 'TITLE' in df.columns:
    df['Genre'] = df.apply(assign_genre, axis=1)
    print("Genre column added successfully!")
else:
    print("Error: 'TITLE' column not found in the dataset.")

# Save the updated dataset with the Genre column
updated_file = "updated_dataset_with_genre.csv"
df.to_csv(updated_file, index=False)
print(f"Updated dataset saved to {updated_file}")