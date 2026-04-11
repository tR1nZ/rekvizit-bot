import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

DB_PATH = "props.db"

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

TOP_K_RESULTS = 50
SIMILARITY_THRESHOLD = 0.42
SEARCH_PAGE_SIZE = 5

# Вставь сюда свой Telegram user_id
HOST_IDS = [837859477]