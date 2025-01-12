from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """
    Configuration class for OAuth environment variables using Pydantic.
    """
    DEBUG: bool = Field(False, env="DEBUG")
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    FACEBOOK_CLIENT_ID: str = Field(..., env="FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET: str = Field(..., env="FACEBOOK_CLIENT_SECRET")
    LINKEDIN_CLIENT_ID: str = Field(..., env="LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: str = Field(..., env="LINKEDIN_CLIENT_SECRET")

    def get_secret_key(self, provider: str):
        if provider == "google":
            return self.GOOGLE_CLIENT_SECRET
        elif provider == "facebook":
            return self.FACEBOOK_CLIENT_SECRET
        elif provider == "linkedin":
            return self.LINKEDIN_CLIENT_SECRET

    class Config:
        env_file = ".env"

try:
    settings = Config()
except ValidationError as e:
    print("Configuration validation error:", e)