from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_key: str
    prompt_id: str
    frontend_origins: str
    openai_url: str

    class Config:
        env_file = ".env"

settings = Settings()
