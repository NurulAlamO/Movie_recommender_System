from db import get_db, query_format
import pandas as pd
import psycopg2
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv("dataset.csv")

data["features"] = data["emotion"] + " " + data["movie"]

tfidf = TfidfVectorizer()
vectors = tfidf.fit_transform(data["features"])
similarity = cosine_similarity(vectors)

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def content_based(movie):
    if movie not in data["movie"].values:
        return []
    idx = data[data["movie"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return [data.iloc[i[0]].movie for i in scores[1:8]]

def user_profile_recommend(username):
    conn = get_db()
    c = conn.cursor()
    query = query_format("SELECT movie FROM favorites WHERE username=?")
    c.execute(query, (username,))
    user_movies = [x[0] for x in c.fetchall()]
    conn.close()
    if not user_movies:
        return data["movie"].sample(5).tolist()
    recs = []
    for m in user_movies:
        recs += content_based(m)
    return list(set(recs) - set(user_movies))[:10]

def hybrid_recommend(username):
    return user_profile_recommend(username)
