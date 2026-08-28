from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Central place for all configuration values.
    Pydantic automatically reads these from the .env file and
    validates their types — if DATABASE_URL is missing, the app
    will fail to start with a clear error instead of failing
    mysteriously later.
    """
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours, reasonable for a demo/portfolio app

    class Config:
        env_file = ".env"

settings = Settings()