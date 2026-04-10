import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")
API_URL = f"{BACKEND_URL}/recipes"

st.set_page_config(
    page_title="Recipe Base - Knowledge Management",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recipe-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📚 Recipe Base")
page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Home", "➕ Add Recipe", "📊 Analytics", "🔍 Search Recipes"]
)

# Initialize session state
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

def fetch_recipes():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch recipes: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")
        return []

def add_recipe(recipe_data):
    try:
        response = requests.post(API_URL, json=recipe_data)
        if response.status_code == 201:
            st.success("✅ Recipe added successfully!")
            return True
        else:
            st.error(f"Failed to add recipe: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_recipe(recipe_id):
    try:
        response = requests.delete(f"{API_URL}/{recipe_id}")
        if response.status_code == 200:
            st.success("✅ Recipe deleted successfully!")
            return True
        else:
            st.error("Failed to delete recipe")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Home Page
if page == "🏠 Home":
    st.markdown('<div class="main-header"><h1>🍳 Recipe Base</h1><p>Your culinary knowledge management system</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Statistics
    recipes = fetch_recipes()
    
    with col1:
        st.metric("📖 Total Recipes", len(recipes))
    with col2:
        if recipes:
            avg_time = sum(r.get('prep_time', 0) for r in recipes) / len(recipes)
            st.metric("⏱️ Avg Prep Time", f"{avg_time:.0f} min")
    with col3:
        unique_authors = len(set(r.get('author', '') for r in recipes))
        st.metric("👨‍🍳 Contributors", unique_authors)
    
    st.header("📋 Recipe Collection")
    
    # Display recipes in grid
    if recipes:
        cols = st.columns(2)
        for idx, recipe in enumerate(recipes):
            with cols[idx % 2]:
                with st.expander(f"🍽️ {recipe['title']} - by {recipe['author']}"):
                    st.markdown(f"""
                    **⏱️ Prep Time:** {recipe['prep_time']} minutes  
                    **🌍 Cuisine:** {recipe['cuisine_type']}  
                    **📊 Difficulty:** {recipe['difficulty']}  
                    
                    **🥗 Ingredients:**  
                    {recipe['ingredients']}
                    
                    **👨‍🍳 Steps:**  
                    {recipe['steps']}
                    """)
                    
                    if st.button(f"🗑️ Delete", key=f"del_{recipe['id']}"):
                        if delete_recipe(recipe['id']):
                            st.rerun()
    else:
        st.info("No recipes yet. Click on 'Add Recipe' to get started!")

# Add Recipe Page
elif page == "➕ Add Recipe":
    st.header("➕ Add New Recipe")
    
    with st.form("add_recipe_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Recipe Title *", placeholder="e.g., Spaghetti Carbonara")
            author = st.text_input("Author Name *", placeholder="Your name")
            cuisine_type = st.selectbox("Cuisine Type", ["Italian", "Chinese", "Mexican", "Indian", "Japanese", "French", "Other"])
        
        with col2:
            prep_time = st.number_input("Preparation Time (minutes) *", min_value=1, max_value=1440, value=30)
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        
        ingredients = st.text_area("Ingredients *", placeholder="List all ingredients (one per line)", height=150)
        steps = st.text_area("Cooking Steps *", placeholder="Describe the cooking process", height=200)
        
        submitted = st.form_submit_button("📤 Submit Recipe")
        
        if submitted:
            if not all([title, author, ingredients, steps]):
                st.error("Please fill in all required fields (*)")
            else:
                recipe_data = {
                    "title": title,
                    "author": author,
                    "cuisine_type": cuisine_type,
                    "prep_time": prep_time,
                    "difficulty": difficulty,
                    "ingredients": ingredients,
                    "steps": steps
                }
                
                if add_recipe(recipe_data):
                    st.balloons()
                    st.rerun()

# Analytics Page
elif page == "📊 Analytics":
    st.header("📊 Recipe Analytics Dashboard")
    
    recipes = fetch_recipes()
    
    if recipes:
        df = pd.DataFrame(recipes)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cuisine distribution
            cuisine_counts = df['cuisine_type'].value_counts()
            fig1 = px.pie(values=cuisine_counts.values, names=cuisine_counts.index, title="Recipes by Cuisine")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Difficulty distribution
            difficulty_counts = df['difficulty'].value_counts()
            fig2 = px.bar(x=difficulty_counts.index, y=difficulty_counts.values, title="Recipes by Difficulty", color=difficulty_counts.index)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Prep time analysis
        fig3 = px.histogram(df, x='prep_time', nbins=20, title="Distribution of Preparation Times", color_discrete_sequence=['#667eea'])
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top authors
        st.subheader("Top Contributors")
        author_counts = df['author'].value_counts().head(10)
        st.bar_chart(author_counts)
        
    else:
        st.info("No data available for analytics")

# Search Page
elif page == "🔍 Search Recipes":
    st.header("🔍 Search Recipes")
    
    search_term = st.text_input("Search by title, author, or cuisine")
    
    if search_term:
        recipes = fetch_recipes()
        filtered_recipes = [
            r for r in recipes 
            if search_term.lower() in r['title'].lower() 
            or search_term.lower() in r['author'].lower()
            or search_term.lower() in r['cuisine_type'].lower()
        ]
        
        if filtered_recipes:
            st.success(f"Found {len(filtered_recipes)} recipes")
            for recipe in filtered_recipes:
                with st.container():
                    st.markdown(f"""
                    <div class="recipe-card">
                        <h3>{recipe['title']}</h3>
                        <p><strong>Author:</strong> {recipe['author']} | <strong>Cuisine:</strong> {recipe['cuisine_type']} | 
                        <strong>Prep Time:</strong> {recipe['prep_time']} min | <strong>Difficulty:</strong> {recipe['difficulty']}</p>
                        <details>
                            <summary>View Recipe</summary>
                            <p><strong>Ingredients:</strong><br>{recipe['ingredients']}</p>
                            <p><strong>Steps:</strong><br>{recipe['steps']}</p>
                        </details>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No recipes found matching your search")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Recipe Base v1.0**  
    Manage your culinary knowledge efficiently  
    
    📝 Created with Streamlit & FastAPI  
    🗄️ Powered by PostgreSQL
    """
)