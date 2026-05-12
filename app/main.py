from fastapi import FastAPI
import hvac
import psycopg2
import os
import random

app = FastAPI(title="Spam Classifier API")

VAULT_URL = os.getenv("VAULT_ADDR", "http://localhost:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "myroot")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ml_database")

def get_db_credentials():
    client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)
    try:
        secret = client.secrets.kv.v2.read_secret_version(path='db_credentials')
    except hvac.exceptions.InvalidPath:
        # Инициализация хранилища (выполняется требование лабы по хардкоду параметров при старте)
        client.secrets.kv.v2.create_or_update_secret(
            path='db_credentials',
            secret=dict(username='ml_user', password='ml_password')
        )
        secret = client.secrets.kv.v2.read_secret_version(path='db_credentials')
    return secret['data']['data']

def save_to_db(text: str, prediction: str):
    creds = get_db_credentials()
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=creds['username'], password=creds['password']
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            message TEXT,
            result VARCHAR(50)
        )
    """)
    cursor.execute("INSERT INTO predictions (message, result) VALUES (%s, %s)", (text, prediction))
    conn.commit()
    cursor.close()
    conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(message: str):
    result = "spam" if random.choice([True, False]) else "ham"
    try:
        save_to_db(message, result)
        db_status = "saved"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {"message": message, "prediction": result, "db_status": db_status}