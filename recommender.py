import pickle
import random
import requests
import os
from ml_recommender import hybrid_recommend
from dotenv import load_dotenv

load_dotenv()

data = pickle.load(open("data.pkl", "rb"))
model = pickle.load(open("model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))

API_KEY = os.getenv("TMDB_API_KEY")

def ml_predict(emotion):
    try:
        encoded = encoder.transform([emotion])
        prediction = model.predict([[encoded[0]]])
        return prediction[0]
    except:
        return None
def get_movies(emotion=None, search=None):

    if search and search.strip():
        search = search.strip().lower()

        movies = data[
            data['movie'].str.lower().str.contains(search, na=False)
        ]['movie'].tolist()

        if not movies:
            movies = data['movie'].sample(5).tolist()

    elif emotion:
        movie = ml_predict(emotion)

        emotion_movies = data[data['emotion'] == emotion]['movie'].tolist()

        if movie and movie in emotion_movies:
            others = [m for m in emotion_movies if m != movie]
            random_movies = random.sample(others, min(4, len(others)))
            movies = [movie] + random_movies
        else:
            movies = random.sample(emotion_movies, min(5, len(emotion_movies)))
    else:
        movies = data['movie'].sample(5).tolist()

    random.shuffle(movies)
    return fetch_movies(movies[:5])

def recommend_from_favorites(username):
    movie_names = hybrid_recommend(username)
    return fetch_movies(movie_names)

movie_cache = {}

def fetch_movies(movie_names):
    final_movies = []

    for name in movie_names:
        if name in movie_cache:
            final_movies.append(movie_cache[name])
            continue

        try:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name}"
            res = requests.get(url, timeout=5)
            data_res = res.json()

            m = data_res["results"][0] if data_res.get("results") else {}
            poster = m.get("poster_path", "")

            movie_data = {
                "title": m.get("title", name),
                "rating": m.get("vote_average", "N/A"),
                "poster": f"https://image.tmdb.org/t/p/w500{poster}" if poster else ""
            }

        except:
            movie_data = {"title": name, "rating": "N/A", "poster": ""}

        movie_cache[name] = movie_data
        final_movies.append(movie_data)

    return final_movies