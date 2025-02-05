import pandas as pd

# Load the file, skipping problematic lines
try:
    df = pd.read_csv("amazon_com_extras.csv", on_bad_lines="skip", encoding="ISO-8859-1")  # Adjust encoding if needed
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
        "Literary Fiction": ["style", "character development", "thematic depth", "literary", "symbolism", "realism", "prose", "narrative", "dialogue", "psychological", "metaphor", "social commentary", "existential", "introspection", "modernism", "complexity", "identity", "artistic", "depth", "self-discovery"],
        "Historical Fiction": ["history", "past", "real events", "fictional characters", "period", "time period", "reconstruction", "realistic", "archaeology", "heritage", "ancient", "cultural context", "revolution", "war", "politics", "age-old", "traditions", "colonial", "historical accuracy", "legacy"],
        "Mystery": ["crime", "investigation", "puzzle", "detective", "clue", "whodunit", "red herring", "suspects", "intrigue", "secrets", "forensics", "sleuth", "suspicion", "unveiling", "hidden truth", "riddles", "alibis", "suspense", "plot twists", "crime scene"],
        "Thriller": ["suspense", "excitement", "danger", "high stakes", "action-packed", "adrenaline", "mystery", "tension", "plot twists", "risk", "heart-pounding", "nail-biting", "psychological", "shocking", "intensity", "cliffhanger", "explosions", "revenge", "secrets", "chase"],
        "Science Fiction": ["futuristic", "space", "technology", "time travel", "aliens", "robots", "cyberpunk", "intergalactic", "utopia", "dystopia", "artificial intelligence", "virtual reality", "space exploration", "parallel universe", "extraterrestrial", "nanotechnology", "genetics", "space opera", "future cities", "high-tech"],
        "Fantasy": ["magic", "mythical creatures", "imaginary worlds", "supernatural", "epic", "dragons", "wizards", "swords", "enchanted", "quests", "magic spells", "prophecy", "royalty", "fantastical", "sorcery", "legendary", "parallel worlds", "monsters", "fairy tale", "adventure"],
        "Adventure": ["action", "quest", "journey", "exploration", "risk", "expedition", "treasure", "discovery", "survival", "wild", "remote places", "danger", "voyage", "adrenaline", "challenges", "heroic", "journey of self", "new frontiers", "overcoming obstacles", "explorers"],
        "Romance": ["love", "relationship", "emotions", "romantic", "hugs", "kisses", "heartbreak", "affection", "commitment", "passion", "chemistry", "marriage", "soulmates", "dating", "attraction", "intimacy", "romantic gestures", "love triangle", "longing", "happy ending"],
        "Horror": ["fear", "supernatural", "creepy", "disturbing", "monsters", "darkness", "terror", "gore", "ghosts", "demons", "haunted", "nightmare", "shock", "jump scares", "paranormal", "psychological", "blood", "evil", "death", "the unknown"],
        "Young Adult (YA)": ["teen", "coming-of-age", "growth", "adolescence", "relationships", "teen angst", "friendship", "identity", "self-discovery", "rebellion", "peer pressure", "first love", "high school", "emotions", "family", "dreams", "independence", "struggles", "romance", "belonging"],
        "Children’s Fiction": ["kids", "imagination", "fun", "innocence", "playful", "adventure", "learning", "friendship", "fairy tale", "magic", "animals", "wholesome", "fantasy", "growth", "play", "creativity", "humor", "family", "curiosity", "morals"],
        "Dystopian": ["post-apocalyptic", "totalitarian", "society", "rebellion", "future", "oppression", "survival", "resistance", "corruption", "war", "chaos", "scarcity", "dark future", "anarchy", "control", "freedom", "collapse", "futuristic", "overthrow", "elite"],
        "Magical Realism": ["magic", "realism", "dreamlike", "surreal", "ordinary meets extraordinary", "myth", "whimsy", "supernatural", "reality bending", "imagination", "enchantment", "metaphysical", "symbolic", "unseen forces", "magical creatures", "poetic", "mysterious", "mood", "paradox", "allegory"],
        "Urban Fantasy": ["magic", "city", "modern world", "supernatural", "fantasy elements", "mystical", "otherworldly", "hidden", "real-life setting", "underground", "mythology", "hidden realms", "fae", "urban legends", "parallel worlds", "ghosts", "demons", "vampires", "magic in the streets", "secret societies"],
        "Historical Romance": ["history", "romance", "past", "love story", "period", "regency", "Victorian", "courtship", "ballrooms", "aristocracy", "sweeping love", "tension", "family drama", "passion", "marriage", "inheritance", "social class", "heir", "nobility", "historical setting"],
        "Action": ["adventure", "high stakes", "explosions", "thrills", "combat", "fighting", "battles", "escape", "revenge", "car chases", "danger", "stunts", "adrenaline", "tension", "survival", "rescue", "assassins", "mercenaries", "secret missions", "tactical"],
        "Satire": ["humor", "criticism", "parody", "irony", "cultural commentary", "mockery", "exaggeration", "political", "absurdity", "social issues", "funny", "wit", "sarcasm", "ridicule", "irony", "lampoon", "comedy", "spoof", "expose", "critique"]
    },
    "Non-Fiction": {
        "Biography": ["life story", "person", "real events", "true account", "personal journey", "accomplishments", "struggles", "family", "legacy", "history", "autobiography", "inspiration", "personal growth", "role model", "memorable", "achievements", "character", "influence", "famous", "impact"],
        "Autobiography": ["self", "personal story", "first-person", "memoir", "life experience", "reflections", "growth", "identity", "career", "challenges", "family", "legacy", "inspiration", "events", "inner thoughts", "self-discovery", "struggles", "successes", "life lessons", "influence"],
        "Memoir": ["memory", "personal", "experiences", "specific events", "reflection", "past", "struggles", "growth", "change", "lesson", "insight", "introspection", "personal journey", "narrative", "emotion", "truth", "self-expression", "vulnerability", "identity", "history"],
        "Self-Help": ["personal growth", "improvement", "motivation", "advice", "well-being", "success", "life coaching", "happiness", "mindfulness", "confidence", "resilience", "empowerment", "goal setting", "positivity", "productivity", "overcoming obstacles", "mental health", "inspiration", "practical advice", "life strategies"],
        "True Crime": ["real crime", "investigation", "criminal case", "murder", "justice", "forensics", "courtroom", "detective", "suspects", "cold cases", "crime scene", "psychology", "law enforcement", "victims", "criminals", "evidence", "trial", "mystery", "criminal justice", "guilt"],
        "Travel": ["journey", "exploration", "places", "adventure", "destinations", "culture", "landmarks", "experiences", "vacation", "wanderlust", "sightseeing", "local cuisine", "history", "tourism", "nature", "exotic", "discovering", "itinerary", "landscapes", "road trip"],
        "Cookbook": ["recipes", "cooking", "food", "ingredients", "chef", "meal planning", "baking", "nutrition", "healthy", "cooking tips", "kitchen", "family meals", "gourmet", "culinary", "seasoning", "dishes", "meal prep", "international cuisine", "vegetarian", "dining"],
        "Health & Wellness": ["fitness", "well-being", "nutrition", "mental health", "exercise", "self-care", "mindfulness", "stress management", "balance", "holistic", "sleep", "meditation", "wellness", "vitamins", "mental clarity", "detox", "workout", "personal growth", "health tips", "prevention"],
        "Psychology": ["mind", "behavior", "emotions", "cognition", "mental processes", "therapy", "mental health", "psychotherapy", "self-esteem", "motivation", "personality", "neuroscience", "emotional intelligence", "mindfulness", "cognitive-behavioral", "psychological theories", "stress", "child development", "relationships", "addiction"],
        "Philosophy": ["existence", "ethics", "knowledge", "reality", "reasoning", "morality", "truth", "logic", "metaphysics", "theology", "human nature", "rationalism", "empiricism", "idealism", "free will", "knowledge", "philosophers", "concepts", "questioning", "mind-body problem"],
        "History": ["past", "events", "timeline", "historical", "figures", "chronicle", "archaeology", "civilizations", "ancient", "wars", "politics", "revolutions", "leaders", "societies", "legacy", "eras", "culture", "historical accuracy", "change", "historical analysis"],
        "Science": ["biology", "physics", "chemistry", "research", "discovery", "innovation", "technology", "experiments", "knowledge", "theories", "natural world", "evolution", "ecology", "astronomy", "medicine", "genetics", "genome", "neuroscience", "climate change", "energy"],
        "Business": ["management", "entrepreneurship", "leadership", "strategy", "corporate", "finance", "marketing", "startups", "growth", "innovation", "branding", "operations", "teamwork", "start-up culture", "vision", "management skills", "business ethics", "investment", "productivity", "consulting"],
        "Technology": ["innovation", "tech", "gadgets", "future", "computing", "software", "hardware", "AI", "cloud", "automation", "big data", "internet", "cybersecurity", "digital transformation", "programming", "networking", "blockchain", "tech industry", "devices", "coding"],
        "Politics": ["government", "policy", "elections", "leaders", "international relations", "democracy", "ideology", "political theory", "parties", "activism", "social justice", "public policy", "rights", "laws", "global affairs", "conservative", "liberal", "government systems", "political movements", "legislation"],
        "Economics": ["money", "markets", "business", "finance", "economic theory", "supply and demand", "global economy", "inflation", "investment", "capitalism", "trade", "monetary policy", "poverty", "wealth distribution", "unemployment", "recession", "economic growth", "interest rates", "taxation", "economic systems"]
    }
}

# Example to access specific genre-related keywords
print(genre_dict["Fiction"]["Romance"])  # Prints the keywords related to Romance genre


# Define a function to assign genre based on TITLE using the genre_dict
def assign_genre(row):
    """
    Assigns a genre to each row based on the TITLE column and the genre_dict.
    """
    title = str(row.get('TITLE', '')).lower()  # Safely handle missing 'TITLE'
    
    # Iterate through the genre dictionary to find the most suitable genre
    for genre_type, genres in genre_dict.items():
        for genre, keywords in genres.items():
            # If any keyword is found in the title, assign the corresponding genre
            if any(keyword in title for keyword in keywords):
                return genre
    return 'Unknown'

# Apply the function to create a new column for Genre
if 'TITLE' in df.columns:
    df['Genre'] = df.apply(assign_genre, axis=1)
    print("Genre column added successfully!")
else:
    print("Error: 'TITLE' column not found in the dataset.")

# Save the updated dataset with the Genre column
updated_file = "updated_dataset_with_genre3.csv"
df.to_csv(updated_file, index=False)
print(f"Updated dataset saved to {updated_file}")