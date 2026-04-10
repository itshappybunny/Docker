from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time

# Retry logic for database connection
def get_db_connection():
    max_retries = 5
    retry_delay = 5
    
    DB_USER = os.getenv("DB_USER", "recipe_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "recipe_password")
    DB_HOST = os.getenv("DB_HOST", "postgres-service")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "recipe_db")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            connection = engine.connect()
            connection.close()
            return engine
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(retry_delay)
    
    raise Exception("Could not connect to database after multiple retries")

engine = get_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()