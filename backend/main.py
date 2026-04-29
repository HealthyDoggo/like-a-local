"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes import tips, locations, jobs, categories, auth, demo
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
app.include_router(demo.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "TravelBuddy Backend API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


_LANGUAGE_METADATA = {
    "en": {"name": "English",    "native_name": "English"},
    "es": {"name": "Spanish",    "native_name": "Español"},
    "fr": {"name": "French",     "native_name": "Français"},
    "de": {"name": "German",     "native_name": "Deutsch"},
    "it": {"name": "Italian",    "native_name": "Italiano"},
    "pt": {"name": "Portuguese", "native_name": "Português"},
    "ru": {"name": "Russian",    "native_name": "Русский"},
    "ja": {"name": "Japanese",   "native_name": "日本語"},
    "ko": {"name": "Korean",     "native_name": "한국어"},
    "zh": {"name": "Chinese",    "native_name": "中文"},
    "ar": {"name": "Arabic",     "native_name": "العربية"},
    "hi": {"name": "Hindi",      "native_name": "हिन्दी"},
    "th": {"name": "Thai",       "native_name": "ภาษาไทย"},
    "vi": {"name": "Vietnamese", "native_name": "Tiếng Việt"},
    "id": {"name": "Indonesian", "native_name": "Bahasa Indonesia"},
}


@app.get("/api/languages")
def get_supported_languages():
    """
    Get list of supported languages for translation.
    Driven by settings.supported_languages so config is the single source of truth.
    """
    languages = [
        {"code": code, **_LANGUAGE_METADATA[code]}
        for code in settings.supported_languages
        if code in _LANGUAGE_METADATA
    ]
    return {"languages": languages}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )

