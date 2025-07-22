import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score
from joblib import dump, load

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fakenews_model.joblib')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.joblib')
DATA_PATH_REAL = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'True.csv')
DATA_PATH_FAKE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Fake.csv')

def train_fake_news_model():
    df_true = pd.read_csv(DATA_PATH_REAL)
    df_fake = pd.read_csv(DATA_PATH_FAKE)

    df_true['label'] = 'REAL'
    df_fake['label'] = 'FAKE'
    df = pd.concat([df_true, df_fake])[['text', 'label']].dropna().sample(frac=1, random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=7)
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
    tfidf_train = vectorizer.fit_transform(X_train)
    tfidf_test = vectorizer.transform(X_test)

    classifier = PassiveAggressiveClassifier(max_iter=50)
    classifier.fit(tfidf_train, y_train)
    y_pred = classifier.predict(tfidf_test)
    acc = accuracy_score(y_test, y_pred)
    print("Accuracy score is : ------>",acc)
    dump(classifier, MODEL_PATH)
    dump(vectorizer, VECTORIZER_PATH)
    return acc

def load_fake_news_model():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
        train_fake_news_model()
    classifier = load(MODEL_PATH)
    vectorizer = load(VECTORIZER_PATH)
    return classifier, vectorizer

def classify_article(text):
    classifier, vectorizer = load_fake_news_model()
    vect_text = vectorizer.transform([text])
    prediction = classifier.predict(vect_text)[0]
    return prediction

if __name__ == "__main__":
    train_fake_news_model()