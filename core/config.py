from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME : str = "Chat Application"


    MONGO_URL : str = "mongodb://localhost:27017"
    DB_NAME : str = "chat_db"
    
    
    JWT_SECRET_KEY : str = "8f6d70fca64fb2ad90d5f6a8de5934783c02204f2b6ff1bdc866fcb3851a6cd8"
    JWT_ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 60 * 60
    

settings = Settings()
