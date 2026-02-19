import os

class Settings:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "shipping-service")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FAILURE_MODE = os.getenv("FAILURE_MODE", "NONE")

settings = Settings()
