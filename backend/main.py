"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes import tips, locations, jobs, categories, auth
from backend.api.routes.locations import promoted_router
from backend.database.connection import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="TravelBuddy Backend API",
    description="Backend API for TravelBuddy travel companion app",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tips.router)
app.include_router(locations.router)
app.include_router(promoted_router)
app.include_router(jobs.router)
app.include_router(categories.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "TravelBuddy Backend API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/languages")
def get_supported_languages():
    """
    Get list of supported languages for translation.

    Returns:
        List of language objects with code, English name, and native name
    """
    return {
        "languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"},
            {"code": "pt", "name": "Portuguese", "native_name": "Português"},
            {"code": "it", "name": "Italian", "native_name": "Italiano"},
            {"code": "zh", "name": "Chinese", "native_name": "中文"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
            {"code": "ar", "name": "Arabic", "native_name": "العربية"},
            {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )

