import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np

# Load pre-trained language model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


df = pd.read_csv('dataset.csv')

# Define personas
subtype_to_persona = {
    'Religious Sites': 'Spiritual Seeker',
    'Historical Sites & Landmarks': 'History Buff',
    'Nature & Parks': 'Nature Enthusiast',
    'Museums': 'Art & Culture Lover',
    'Shopping': 'Shopaholic',
    'Tours & Adventures': 'Adventurer',
    'Restaurants (Food & Dining)': 'Foodie',
    'Wellness & Fitness': 'Health Conscious',
    'Miscellaneous': 'Explorer',
    'Entertainment': 'Entertainment Seeker'
}

def get_persona(preferred_subtype):
    """Map user's preferred subtype to a persona."""
    return subtype_to_persona.get(preferred_subtype, "Explorer")

def filter_and_prepare_data(preferred_subtype):
    
    required_columns = ['subtype', 'description_x', 'text', 'travel_style', 'budget', 'age_group']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")
    
    """Filter dataset based on user preferences (theme) and prepare text for TF-IDF."""
    
    if isinstance(df, pd.DataFrame):  # Ensure df is a DataFrame    
        # Check if preferred_subtype is a valid string
        if not isinstance(preferred_subtype, str):
            raise ValueError(f"Expected 'preferred_subtype' to be a string, got {type(preferred_subtype)}")
        
        # Filter by theme
        print(f"Filtering data for subtype: {preferred_subtype}")  # Debug log
        filtered_df = df[df['subtype'].str.lower().str.contains(preferred_subtype.lower(), na=False)]
        
        print(f"Filtered DataFrame shape: {filtered_df.shape}")  # Debug log

        # Combine text
        filtered_df.loc[:, 'combined_text'] = (
            filtered_df['description_x'].fillna('') + " " + filtered_df['text'].fillna('')
        ).str.strip()

        if filtered_df.empty:
            print("No matching places found for your preferences.")  # Debug log
            return None
        else:
            filtered_df = filtered_df.drop_duplicates(subset=['id'], keep='first').copy()
            return filtered_df
    else:
        print("Error: df is not a valid DataFrame!")  # Debug log
        return None

def compute_embeddings(texts):
    return embedding_model.encode(texts, convert_to_tensor=True)

def handle_user_feedback(recommendations, user_preferences):
    for index, row in recommendations.iterrows():
        feedback = input(f"Do you like '{row['name']}'? (yes/no): ").strip().lower()
        if feedback == "yes":
            if "liked_places" not in user_preferences:
                user_preferences["liked_places"] = []
            user_preferences["liked_places"].append(row['name'])



def recommend(preferred_subtype, keywords, travel_style=None, budget=None, age_group=None):
    # Ensure keywords is a list (if it's a string, split it)
    if isinstance(keywords, str):
        keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
    
    # Create user preferences dictionary
    user_preferences = {
        'subtype': preferred_subtype,
        'keywords': keywords,
        'age_group': age_group,
        'travel_style': travel_style,
        'budget': budget
    }
    
    # Get persona (don't overwrite user_preferences)
    persona = get_persona(preferred_subtype)
    filtered_df = filter_and_prepare_data(preferred_subtype)

    if filtered_df is None:
        return []
    
    combined_texts = filtered_df['combined_text'].tolist()
    item_embeddings = compute_embeddings(combined_texts)

    # Handle empty keywords case
    user_query = " ".join(user_preferences['keywords']) if user_preferences['keywords'] else ""
    user_embedding = compute_embeddings([user_query])[0]

    similarities = util.cos_sim(user_embedding, item_embeddings)[0].cpu().numpy()
    filtered_df['similarity'] = similarities
    
    # Add boost score calculation
    def calculate_boost(row):
        boost = 0
        if travel_style and pd.notna(row.get('travel_style')) and travel_style.lower() in str(row['travel_style']).lower():
            boost += 0.1  
            print("travel_style + 0.1, boost=", boost)
        if budget and pd.notna(row.get('budget')) and budget.lower() in str(row['budget']).lower():
            boost += 0.1
            print("budget + 0.1, boost=", boost)
        if age_group and pd.notna(row.get('age_group')) and age_group.lower() in str(row['age_group']).lower():
            boost += 0.1
            print("age_group + 0.1, boost=", boost)
        return boost

    filtered_df['boost'] = filtered_df.apply(calculate_boost, axis=1)
    filtered_df['final_score'] = filtered_df['similarity'] + filtered_df['boost']

    # Sort by final score and get top recommendations
    recommendations = filtered_df.sort_values(by='final_score', ascending=False).head(10)

    return recommendations[[
        'id', 'name', 'city', 'subtype', 'description_x',
        'imageUrl_x', 'placeRating', 'website', 'budget', 
        'travel_style', 'age_group'
    ]].to_dict(orient='records')

