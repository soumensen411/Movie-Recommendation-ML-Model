# CineMatch AI — Movie Recommendation ML Model

CineMatch AI is a compact movie-recommendation project that finds similar films using simple content-based techniques. It powers a polished Streamlit frontend to let users search a movie and get five high-quality recommendations with poster previews fetched from TMDB.

# Key points
- Core idea: build a tags-based content representation for each movie, compute cosine similarity, and return the top matches.
- Interface: Streamlit app (Frontend/app.py) named "CineMatch AI".
- Notebook: a Jupyter notebook (Notebook/Movie_Recomendation.ipynb) contains the exploratory work and model-building steps.
- Data: a TMDB-derived dataset (Notebook/tmdb_5000_movies.csv) and a preprocessed movies list used by the app (Frontend/movies_list.pkl).

# Features
- Searchable movie list and single-click recommendations (top 5).
- On-the-fly similarity computation using CountVectorizer + cosine similarity.
- Poster fetching from TMDB to display visual results.
- Clean, modern Streamlit UI with responsive movie cards and match scores.

# How it works (high level)
1. The app loads a serialized movies list (movies_list.pkl) containing movie_id, title, and a 'tags' text field.
2. CountVectorizer transforms the 'tags' into token vectors and cosine similarity is computed between movies.
3. Given a selected movie, the app returns the 5 most similar movies by similarity score.
4. For each recommended movie, the app requests the poster image from the TMDB API and displays it in the UI.

# Quick run (frontend demo)
- The Streamlit app is located at `Frontend/app.py`. From the Frontend directory you can run:
  - streamlit run app.py
- The app expects a preprocessed `movies_list.pkl` (present in `Frontend/`) and uses TMDB for poster images. The current code uses a TMDB key inline — you should replace this with a secure configuration (environment variable) in production.

Important files
- Notebook/Movie_Recomendation.ipynb — exploratory analysis, feature engineering, and model prototyping.
- Notebook/tmdb_5000_movies.csv — source dataset (TMDB export).
- Frontend/app.py — Streamlit application (UI + recommendation logic).
- Frontend/movies_list.pkl — preprocessed movie dictionary used by the app.
- Frontend/requirements.txt — Python dependencies for the frontend (Streamlit, scikit-learn, pandas, requests, etc).

Notes & recommendations
- TMDB API: The app fetches posters from TMDB. The code currently includes a hardcoded API key; replace this with an environment variable (and revoke/regenerate the current key if it's real).
- Preprocessing: The project stores a precomputed movies_list.pkl to speed up loading in the UI; the notebook shows how tags are built and combined.
- Reproducibility: If you want to reproduce or update the movies_list.pkl from the CSV, re-run the notebook preprocessing steps and serialize the resulting dictionary/dataframe.

# Possible next steps
- Replace the inline TMDB key with a secure env-var-driven configuration.
- Add caching or a lightweight API layer to avoid repeated poster requests.
- Experiment with different embedding strategies (e.g., TF-IDF, word embeddings, or fine-tuned sentence embeddings) for improved recommendation quality.
- Add unit tests around the recommend() logic and poster-fetching behavior.

