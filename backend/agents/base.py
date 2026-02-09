"""Base agent utilities for VacanceAI"""
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings


def get_llm(model: str = "gemini-2.0-flash", temperature: float = 0.7):
    """Get configured LLM instance"""
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.google_api_key,
        temperature=temperature
    )
