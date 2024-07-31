from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_source: str = "yahoo_financea"
    redis_url: str = "redis://localhost:6379"
    postgres_url: str = "postgresql://user:password@localhost/dbname"

    class Config:
        env_file = ".env"


settings = Settings()
