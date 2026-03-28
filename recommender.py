import pickle
import random
import requests
import os
from ml_recommender import hybrid_recommend

data = pickle.load(open("data.pkl", "rb"))
API_KEY = os.getenv("TMDB_API_KEY")

def get_movies(emotion=None, search=None):
    if search:
        movies = data[data['movie'].str.contains(search, case=False)]['movie'].tolist()
    elif emotion:
        movies = data[data['emotion'] == emotion]['movie'].tolist()
    else:
        movies = data['movie'].tolist()
    random.shuffle(movies)
    return fetch_movies(movies[:5])

def recommend_from_favorites(username):
    movie_names = hybrid_recommend(username)
    return fetch_movies(movie_names)

def fetch_movies(movie_names):
    final_movies = []
    for name in movie_names:
        try:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}"
            res = requests.get(url, timeout=5)
            data_json = res.json()
            if data_json.get("results"):
                m = data_json["results"][0]
                poster = m.get("poster_path")
                final_movies.append({
                    "title": m.get("title", name),
                    "rating": m.get("vote_average", "N/A"),
                    "poster": f"https://image.tmdb.org/t/p/w500{poster}" if poster else ""
                })
            else:
                final_movies.append({"title": name, "rating": "N/A", "poster": ""})
        except:
            final_movies.append({"title": name, "rating": "N/A", "poster": ""})
    return final_movies