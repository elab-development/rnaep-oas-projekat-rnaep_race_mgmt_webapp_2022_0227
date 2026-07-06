import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    race_database_url: str = os.getenv(
        "RACE_DATABASE_URL", "postgresql://obstarace:obstarace@localhost:5434/race_db"
    )


config = Config()
