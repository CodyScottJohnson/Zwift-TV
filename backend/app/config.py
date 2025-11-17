import os
from typing import Final


class BaseConfig:
    SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "dev")
    DEBUG = False

    # For CORS – override per env if needed
    API_CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "http://localhost:3009").split(",")
    ROKU_IP = os.getenv("ROKU_IP")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
