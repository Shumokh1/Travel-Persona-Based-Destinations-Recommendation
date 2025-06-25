# Travel-Persona-Based-Destinations-Recommendation

## 📘 Overview
This senior project is a smart tourism recommendation system designed to help users discover personalized tourist destinations across Saudi Arabia. Using **Natural Language Processing (NLP)** and **Machine Learning (ML)** techniques, the system recommends places based on user preferences, promoting local tourism in line with **Saudi Vision 2030**.

---

## 🎯 Objectives
- Recommend Saudi tourist attractions based on user preferences.
- Utilize user input with NLP to understand interests.
- Use data science and ML to generate accurate suggestions.
- Visualize tourism trends and insights for analysis.
- Provide an easy-to-use interface for users to explore Saudi Arabia.

---

## 📊 Dataset

- A high-quality dataset was manually collected from various platforms and includes over 20,000 destination records.
- The dataset was cleaned and preprocessed to remove duplicates, correct inconsistencies, and format it for efficient use in recommendations.
- It contains destination names, descriptions, categories, and ratings, and can be used for further tourism analytics such as trend analysis or geolocation studies.

## 🧠 Model

Technique: Content-based filtering enhanced with pre-trained MiniLM (SentenceTransformer)

Steps:

- User Input: Preferred theme and keywords describing desired destination

- Data Filtering: Apply filters based on user criteria (e.g., budget, age)

- Text Embedding: Generate semantic embeddings for user input and destination data using MiniLM

- Similarity Calculation: Compute cosine similarity between user and destination embeddings

- Score Boosting: Increase similarity by +0.1 for each matching attribute (travel style, age group, budget)

- Output: Return ranked destinations with similarity scores matching user preferences
## 🖥️ Web Interface

- The web interface allows users to interact with the system in a simple and accessible way.
- It collects user preferences and displays the recommended destinations without needing a server-side backend.

### Sample Output

Below is a preview of the main functionality offered by our application:

<img src="https://github.com/Shumokh1/Travel-Persona-Based-Destinations-Recommendation/raw/main/example.png" width="350" alt="ML Model" />
