"""LangChain-based agent: builds the LLM (provider-agnostic - OpenAI or Ollama,
selected via .env) and runs the briefing chain (prompt | llm | output parser).
"""
from langchain_core.output_parsers import StrOutputParser

from agent.prompts import build_prompt
from config import config


class UnsupportedProviderError(Exception):
    pass


def _build_llm():
    provider = config.llm_provider

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not config.openai_api_key:
            raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set in .env")
        return ChatOpenAI(model=config.openai_model, api_key=config.openai_api_key, temperature=0.3)

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=config.ollama_model, base_url=config.ollama_base_url, temperature=0.3)

    raise UnsupportedProviderError(
        f"Unknown LLM_PROVIDER '{provider}'. Supported providers: 'openai', 'ollama'."
    )


def generate_briefing(race_data: dict, weather_summary: str) -> str:
    """Runs the structured prompt through the configured LLM and returns Markdown text."""
    llm = _build_llm()
    prompt = build_prompt()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({**race_data, "weather_summary": weather_summary})
