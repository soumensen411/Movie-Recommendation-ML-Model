"""CineMatch AI backend.

Runs the same recommendation logic as the Streamlit app (app.py): CountVectorizer
on the tags, cosine similarity, the 5 closest movies after the selected one.
Nothing is precomputed. Each request calculates similarity for the selected movie.

    pip install -r requirements.txt
    python server.py          # then open http://127.0.0.1:5000
"""
import os
import pickle
import random
from functools import lru_cache

import pandas as pd
import requests
from flask import Flask, abort, jsonify, request, send_from_directory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HERE = os.path.dirname(os.path.abspath(__file__))

# Key from the original app.py. Set TMDB_API_KEY to use your own (and revoke this one).
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")

app = Flask(__name__)

# ----------------------------------------------------------------- model (loaded once)
movies_df = pd.DataFrame(pickle.load(open(os.path.join(HERE, "movies_list.pkl"), "rb")))
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies_df["tags"])  # sparse; similarity is computed per request

# Streamlit's selectbox lists every row, but picks the first row for a repeated title
first_index = {}
for i, t in enumerate(movies_df["title"]):
    first_index.setdefault(t, i)


def recommend(movie):
    movie_index = first_index[movie]
    distances = cosine_similarity(vectors[movie_index], vectors)[0]
    ranked = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    results = []
    for i, score in ranked:
        row = movies_df.iloc[i]
        results.append({
            "title": row.title,
            "id": int(row.movie_id),
            "score": min(int(score * 100), 99),
        })
    return {
        "selected": {"title": movie, "id": int(movies_df.iloc[movie_index].movie_id)},
        "results": results,
        "compared_with": len(movies_df) - 1,
        "vocabulary": len(cv.vocabulary_),
    }


@lru_cache(maxsize=2048)
def fetch_poster(movie_id):
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=5,
        )
        path = r.json().get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{path}" if path else None
    except Exception:
        fetch_poster.cache_clear()  # do not keep a failure around
        return None


# ----------------------------------------------------------------- API
@app.get("/api/movies")
def api_movies():
    return jsonify(list(first_index.keys()))


@app.get("/api/recommend")
def api_recommend():
    title = request.args.get("title", "")
    if title not in first_index:
        abort(404, description="Unknown title")
    return jsonify(recommend(title))


@app.get("/api/sample")
def api_sample():
    """A few random movies from the catalog, used for the poster wall on the home screen."""
    n = min(max(request.args.get("n", 16, type=int), 1), 32)
    titles = random.sample(list(first_index), n)
    return jsonify([
        {"title": t, "id": int(movies_df.iloc[first_index[t]].movie_id)} for t in titles
    ])


@app.get("/api/poster/<int:movie_id>")
def api_poster(movie_id):
    return jsonify({"url": fetch_poster(movie_id)})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": e.description}), 404


# ----------------------------------------------------------------- frontend
@app.get("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.get("/style.css")
def style_css():
    return send_from_directory(HERE, "style.css", mimetype="text/css")


@app.get("/app.js")
def app_js():
    return send_from_directory(HERE, "app.js", mimetype="text/javascript")


@app.get("/favicon.svg")
def favicon():
    return send_from_directory(HERE, "favicon.svg", mimetype="image/svg+xml")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)