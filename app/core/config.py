import json
import os
from dotenv import load_dotenv

load_dotenv()

class EnvVariables:
    API_PORT = os.getenv('API_PORT')

    # DB
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_CLASSNAME = os.getenv("DB_CLASSNAME")
    DB_PORT = os.getenv("DB_PORT")

    FEED_API_BASE_URL = os.getenv("FEED_API_BASE_URL")
    FEED_API_KEY = os.getenv("FEED_API_KEY")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_URL = os.getenv("GEMINI_API_URL")

    SAMPLE_TAGS = json.loads(os.getenv("SAMPLE_TAGS", "[]"))
    SAMPLE_MESSAGES = json.loads(os.getenv("SAMPLE_MESSAGES", "[]"))

    @staticmethod
    def get_routes_by_prefix(prefix):
        """주어진 prefix로 시작하는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.startswith(prefix):
                routes.append(value)
        return routes

    @staticmethod
    def get_routes_by_postfix(postfix):
        """주어진 postfix로 끝나는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.endswith(postfix):
                routes.append(value)
        return routes
