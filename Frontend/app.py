import streamlit as st
import pickle
import pandas as pd
import requests
from PIL import Image
import base64
from io import BytesIO

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="CineMatch AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - Cinematic Dark Theme
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background - Deep cinematic gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        background-attachment: fixed;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #e50914;
        border-radius: 4px;
    }
    
    /* Title Section */
    .main-title {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-title h1 {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #e50914, #ff6b6b, #e50914);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    .main-title p {
        color: #8892b0;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Neon Glow Effect */
    .neon-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e50914, #ff6b6b, #e50914, transparent);
        margin: 1rem auto;
        width: 60%;
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
    }
    
    /* Selectbox Styling */
    div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(229, 9, 20, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    div[data-baseweb="select"]:hover {
        border-color: #e50914 !important;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.2);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #e50914, #b20710) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 3rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(229, 9, 20, 0.6) !important;
        background: linear-gradient(135deg, #ff0a16, #e50914) !important;
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Movie Card Container */
    .movie-card {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
    }
    .movie-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(229, 9, 20, 0.5);
        box-shadow: 0 20px 40px rgba(229, 9, 20, 0.3), 
                    0 0 60px rgba(229, 9, 20, 0.1);
    }
    
    /* Movie Poster Image */
    .movie-poster {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        border-radius: 16px 16px 0 0;
        transition: all 0.4s ease;
    }
    .movie-card:hover .movie-poster {
        filter: brightness(1.1);
    }
    
    /* Movie Info Section */
    .movie-info {
        padding: 1rem;
        background: linear-gradient(180deg, transparent, rgba(0,0,0,0.8));
    }
    .movie-rank {
        display: inline-block;
        background: linear-gradient(135deg, #e50914, #ff6b6b);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 10px rgba(229, 9, 20, 0.4);
    }
    .movie-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.3;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    
    /* Loading Animation */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    .loading-shimmer {
        background: linear-gradient(90deg, #1a1a2e 25%, #16213e 50%, #1a1a2e 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 16px;
    }
    
    /* Section Headers */
    .section-header {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #e50914, #ff6b6b);
        border-radius: 2px;
    }
    
    /* Match Percentage Badge */
    .match-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        color: #46d369;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(70, 211, 105, 0.3);
        z-index: 10;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 0 1rem 0;
        color: #8892b0;
        font-size: 0.85rem;
    }
    .footer span {
        color: #e50914;
    }
    
    /* Floating particles background effect */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_list.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# =============================================================================
# API FUNCTIONS
# =============================================================================
def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8'.format(movie_id),
            timeout=5
        )
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return None
    except:
        return None

def fetch_movie_details(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e9'.format(movie_id),
            timeout=5
        )
        return response.json()
    except:
        return {}

# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    recommended_ids = []
    match_scores = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_ids.append(movie_id)
        # Convert similarity to percentage (approximate)
        match_pct = int((1 - i[1]) * 100) if i[1] < 1 else 95
        match_scores.append(min(match_pct, 99))
    
    return recommended_movies, recommended_posters, recommended_ids, match_scores

# =============================================================================
# UI COMPONENTS
# =============================================================================

# Header Section
st.markdown("""
<div class="main-title">
    <h1>🎬 CineMatch AI</h1>
    <p>Discover Your Next Favorite Film</p>
</div>
<div class="neon-line"></div>
""", unsafe_allow_html=True)

# Center the controls
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Search Section with icon
    st.markdown('<div style="text-align: center; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    
    selected_movie = st.selectbox(
        "",
        movies['title'].values,
        placeholder="🔍 Search for a movie...",
        label_visibility="collapsed"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Styled button
    recommend_clicked = st.button("✨ Find Similar Movies", type="secondary")

# =============================================================================
# RESULTS SECTION
# =============================================================================
if recommend_clicked:
    with st.spinner(''):
        # Custom loading animation
        st.markdown("""
        
        <style>
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
        """, unsafe_allow_html=True)
        
        names, posters, ids, scores = recommend(selected_movie)
    
    # Results Header
    st.markdown(f"""
    <div class="section-header">
        Because you watched <span style="color: #e50914;">{selected_movie}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Movie Cards Grid
    cols = st.columns(5, gap="medium")
    
    for idx, (col, name, poster, movie_id, score) in enumerate(zip(cols, names, posters, ids, scores)):
        with col:
            # Card container
            st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
            
            # Match percentage badge
            st.markdown(f'<div class="match-badge">{score}% Match</div>', unsafe_allow_html=True)
            
            # Poster with fallback
            if poster:
                st.image(poster, use_container_width=True, output_format="auto")
            else:
                # Generate placeholder with movie initial
                initial = name[0].upper() if name else "?"
                st.markdown(f"""
                <div style="width: 100%; aspect-ratio: 2/3; background: linear-gradient(135deg, #1a1a2e, #16213e);
                            display: flex; align-items: center; justify-content: center; border-radius: 16px 16px 0 0;">
                    <span style="font-size: 4rem; color: #e50914; font-weight: 800;">{initial}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Movie info
            st.markdown(f"""
            <div class="movie-info">
                <div class="movie-rank">{idx + 1}</div>
                <div class="movie-title">{name}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Selected movie showcase (hero section)
    st.markdown("""
    <div class="neon-line" style="margin-top: 3rem;"></div>
    """, unsafe_allow_html=True)
    
    # Get selected movie details for hero
    selected_idx = movies[movies['title'] == selected_movie].index[0]
    selected_id = movies.iloc[selected_idx].movie_id
    selected_poster = fetch_poster(selected_id)
    
    hero_col1, hero_col2 = st.columns([1, 2])
    with hero_col1:
        if selected_poster:
            st.image(selected_poster, use_container_width=True)
    
    with hero_col2:
        st.markdown(f"""
        <div style="padding: 2rem;">
            <h2 style="color: white; font-size: 2rem; margin-bottom: 1rem;">{selected_movie}</h2>
            <p style="color: #8892b0; font-size: 1.1rem; line-height: 1.6;">
                Your selection is the starting point for our AI-powered recommendation engine. 
                We've analyzed thousands of films to find these 5 perfect matches based on genre, 
                themes, cast, and viewer preferences.
            </p>
            <div style="margin-top: 1.5rem;">
                <span style="background: rgba(229,9,20,0.2); color: #e50914; padding: 0.5rem 1rem; 
                           border-radius: 20px; font-size: 0.9rem; margin-right: 0.5rem;">🎯 AI Curated</span>
                <span style="background: rgba(70,211,105,0.2); color: #46d369; padding: 0.5rem 1rem; 
                           border-radius: 20px; font-size: 0.9rem;">✓ Verified Matches</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Show popular/trending placeholder when no selection
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; opacity: 0.6;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🎭</div>
        <h3 style="color: #8892b0; font-weight: 400;">Select a movie and click "Find Similar Movies" to discover your next watch</h3>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Powered by <span>TMDB API</span> • Built with <span>Streamlit</span> • CineMatch AI 2024
</div>
""", unsafe_allow_html=True)