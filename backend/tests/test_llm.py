from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings


def test_gemini_connection():

    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=100,
    )

    response = llm.invoke(
        "Reply with exactly: Voyager connection successful"
    )

    assert response.content is not None
    assert "Voyager" in response.content