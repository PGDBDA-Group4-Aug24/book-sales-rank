import pandas as pd
import re

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
        "Magical Realism": ["magic", "realism", "dreamlike", "surreal", "ordinary meets extraordinary"],
        "Urban Fantasy": ["magic", "city", "modern world", "supernatural", "fantasy elements"],
        "Historical Romance": ["history", "romance", "past", "love story", "period"],
        "Action": ["adventure", "high stakes", "explosions", "thrills", "combat"],
        "Satire": ["humor", "criticism", "parody", "irony", "cultural commentary"]
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
        "Science": ["biology", "physics", "chemistry", "research", "discovery", "innovation"],
        "Business": ["management", "entrepreneurship", "leadership", "strategy", "corporate"],
        "Technology": ["innovation", "tech", "gadgets", "future", "computing"],
        "Politics": ["government", "policy", "elections", "leaders", "international relations"],
        "Economics": ["money", "markets", "business", "finance", "economic theory"]
    }
}

# Define a function to assign genre based on TITLE using the genre_dict with regex matching
def assign_genre(row):
    """
    Assigns a genre to each row based on the TITLE column and the genre_dict using regex for keyword matching.
    """
    title = str(row.get('TITLE', '')).lower()  # Safely handle missing 'TITLE'
    
    # Iterate through the genre dictionary to find the most suitable genre
    for genre_type, genres in genre_dict.items():
        for genre, keywords in genres.items():
            # Create a regex pattern that matches any of the keywords, allowing for approximation
            # The pattern matches the keyword as a whole word, case insensitive
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            
            # If any keyword is found in the title, assign the corresponding genre
            if re.search(pattern, title, flags=re.IGNORECASE):
                return genre
    return 'Unknown'

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