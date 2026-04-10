from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    ingredients = Column(Text, nullable=False)  # JSON string or text with ingredients
    steps = Column(Text, nullable=False)        # Cooking steps
    author = Column(String(100), nullable=False)
    prep_time = Column(Integer, nullable=False)  # in minutes
    cuisine_type = Column(String(50), default="Other")
    difficulty = Column(String(20), default="Medium")  # Easy, Medium, Hard
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "author": self.author,
            "prep_time": self.prep_time,
            "cuisine_type": self.cuisine_type,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }