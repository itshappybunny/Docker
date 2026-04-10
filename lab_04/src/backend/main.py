from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Recipe
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Base API",
    description="API for managing recipes and cooking algorithms",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    ingredients: str = Field(..., min_length=1)
    steps: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    prep_time: int = Field(..., gt=0, le=1440)
    cuisine_type: Optional[str] = "Other"
    difficulty: Optional[str] = "Medium"

class RecipeResponse(RecipeCreate):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    ingredients: Optional[str] = None
    steps: Optional[str] = None
    author: Optional[str] = None
    prep_time: Optional[int] = None
    cuisine_type: Optional[str] = None
    difficulty: Optional[str] = None

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.get("/")
def root():
    return {"message": "Recipe Base API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/recipes", response_model=List[RecipeResponse])
def get_recipes(
    skip: int = 0, 
    limit: int = 100,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Recipe)
    
    if cuisine:
        query = query.filter(Recipe.cuisine_type == cuisine)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    
    recipes = query.offset(skip).limit(limit).all()
    return [recipe.to_dict() for recipe in recipes]

@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe.to_dict()

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.to_dict()

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_update: RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    update_data = recipe_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recipe, field, value)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe.to_dict()

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}

@app.get("/recipes/stats/summary")
def get_statistics(db: Session = Depends(get_db)):
    total_recipes = db.query(Recipe).count()
    cuisine_stats = db.query(Recipe.cuisine_type, func.count(Recipe.id)).group_by(Recipe.cuisine_type).all()
    difficulty_stats = db.query(Recipe.difficulty, func.count(Recipe.id)).group_by(Recipe.difficulty).all()
    
    return {
        "total_recipes": total_recipes,
        "by_cuisine": [{"cuisine": c[0], "count": c[1]} for c in cuisine_stats],
        "by_difficulty": [{"difficulty": d[0], "count": d[1]} for d in difficulty_stats]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)