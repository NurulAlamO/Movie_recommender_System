import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import pickle

data = pd.read_csv("dataset.csv")
le = LabelEncoder()
data['emotion_encoded'] = le.fit_transform(data['emotion'])

X = data[['emotion_encoded']]
y = data['movie']

model = DecisionTreeClassifier()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(le, open("encoder.pkl", "wb"))
pickle.dump(data, open("data.pkl", "wb"))   #  IMPORTANT
print("Model Ready!")