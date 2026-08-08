from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Voyager AI"
    VERSION: str = "0.1.0"

    OPENROUTER_API_KEY: str
    MODEL_NAME: str
    OPENROUTER_BASE_URL: str

    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    TAVILY_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()