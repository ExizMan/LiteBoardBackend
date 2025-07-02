from pydantic_settings import BaseSettings
from pydantic import Field


from typing import List

class Settings(BaseSettings):
    POSTGRES_HOST: str = Field(default="127.0.0.1")
    POSTGRES_NAME: str = Field(default="")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_PORT: str = Field(default="5432")
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://89.104.68.136:5173"])

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"

settings = Settings()