from fastapi import FastAPI
from src.routes import router

# Create FastAPI application
app = FastAPI(
    title="ATS Resume Analyzer API",
    description="AI-powered ATS-friendly resume analyzer with semantic chunking and consistency checking",
    version="1.0.0"
)

# Include router from src/routes.py
app.include_router(router)

