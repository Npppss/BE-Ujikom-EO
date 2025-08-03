from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Organizer"
    DATABASE_URL: str
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")  # 30 menit
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")  # 7 hari
    
    # Email settings for forgot password
    SMTP_SERVER: str = Field(default="smtp.gmail.com", alias="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, alias="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", alias="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", alias="SMTP_PASSWORD")
    FROM_EMAIL: str = Field(default="", alias="FROM_EMAIL")
    
    # Frontend URL for password reset
    FRONTEND_URL: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")

    class Config:
        env_file = ".env"
        extra = "forbid"
        allow_population_by_field_name = True

settings = Settings()

# Export variabel agar bisa diimpor langsung
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
