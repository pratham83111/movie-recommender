import streamlit as st
import pickle
import pandas as pd
import requests
import time

API_KEY = "69588d3d79f502cae29f8d55dbc57ad7"

# --------------------------- PAGE CONFIG --------------------------- #
st.set_page_config(page_title="🎬 Movie Recommender – Hotstar Mode", layout="wide")

# --------------------------- HOTSTAR STYLE CSS --------------------------- #
st.markdown("""
<style>
/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0b1120 0%, #090d18 100%);
    color: #e6f1ff;
    font-family: 'Segoe UI', sans-serif;
}
/* Title */
h1 {
    text-align: center;
    font-weight: 800;
    color: #1db9ff;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
/* Subheading */
.subtitle {
    text-align: center;
    color: #9fb3c8;
    margin-bottom: 25px;
}
/* Search Bar */
input[type="text"] {
    background-color: #111927 !important;
    color: #1db9ff !important;
    border: 1px solid #1db9ff !important;
    border-radius: 6px;
    padding: 10px;
}
/* Button */
button[kind="secondary"] {
    background-color: #1db9ff !important;
    color: #fff !important;
    font-weight: bold;
    border-radius: 6px;
}
button[kind="secondary"]:hover {
    background-color: #00bfff !important;
}
/* Movie Card */
.movie-card {
    background-color: #111927;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 0 10px rgba(0,191,255,0.3);
    transition: transform 0.2s;
}
.movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(0,191,255,0.5);
}
.movie-title {
    color: #1db9ff;
    font-weight: 600;
    text-align: center;
    margin-top: 8px;
}
.movie-info {
    color: #9fb3c8;
    text-align: center;
    font-size: 13px;
}
a {
    color: #1db9ff !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------- FETCH MOVIE DETAILS --------------------------- #
def fetch_movie_details(movie_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=videos&language=en-US"
            res = requests.get(url, timeout=8)
            res.raise_for_status()
            data = res.json()
            title = data.get("title", "Unknown Title")
            overview = data.get("overview", "No overview available.")
            poster = data.get("poster_path")
            release_date = data.get("release_date", "N/A")
            year = release_date.split("-")[0] if release_date else "N/A"
            rating = data.get("vote_average", "N/A")
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster}" if poster else "https://via.placeholder.com/300x450?text=No+Image"

            # Trailer
            videos = data.get("videos", {}).get("results", [])
            trailer_key = None
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                    trailer_key = v.get("key")
                    break
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None

            return {"title": title, "poster": poster_url, "overview": overview, "rating": rating, "year": year, "trailer": trailer_url}

        except Exception:
            time.sleep(1)
            continue
    return {"title": "N/A", "poster": "https://via.placeholder.com/300x450?text=No+Image", "overview": "N/A", "rating": "N/A", "year": "N/A", "trailer": None}

# --------------------------- RECOMMEND FUNCTION --------------------------- #
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:9]
    rec = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        rec.append(fetch_movie_details(movie_id))
    return rec

# --------------------------- LOAD DATA --------------------------- #
movies_dict = pickle.load(open("movie_dict.pkl","rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl","rb"))

# --------------------------- UI --------------------------- #
st.markdown("<h1>🎬 Movie Recommender – Hotstar Style</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your personalized movie zone, styled like Disney+ Hotstar 💙</p>", unsafe_allow_html=True)

search = st.text_input("🔍 Search Movie Name:")
if search:
    filtered = movies[movies["title"].str.contains(search, case=False, na=False)]
    if filtered.empty:
        st.warning("No movie found! Try another.")
        st.stop()
    else:
        selected = st.selectbox("🎞 Select a Movie", filtered["title"].values)
else:
    selected = st.selectbox("🎞 Select a Movie", movies["title"].values)

if st.button("Recommend"):
    st.subheader(f"💫 Recommended Movies similar to **{selected}**:")
    rec = recommend(selected)

    # Show posters in slider-like grid (4 per row)
    for i in range(0, len(rec), 4):
        cols = st.columns(4)
        for col, m in zip(cols, rec[i:i+4]):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                st.image(m["poster"], use_container_width=True)
                st.markdown(f"<p class='movie-title'>{m['title']} ({m['year']})</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='movie-info'>⭐ {m['rating']}</p>", unsafe_allow_html=True)
                if m["trailer"]:
                    st.markdown(f"[▶ Watch Trailer]({m['trailer']})", unsafe_allow_html=True)
                st.markdown(f"<p class='movie-info'>{m['overview'][:180]}...</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
