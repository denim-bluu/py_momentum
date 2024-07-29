from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_source: str = "yahoo_finance"


settings = Settings()
