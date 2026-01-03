"""
PC Processing Service for TravelBuddy

This FastAPI service runs on the PC and handles ML model processing:
- Language detection
- Translation (NLLB)
- Embedding generation (miniLM-v6)

The Raspberry Pi sends HTTP requests to this service for processing.
"""
import logging
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import services
# Note: These need to be imported from the backend package
# Make sure the backend directory is in Python path or install as package
import sys
import os

# Add backend directory to path if not already there
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.services.translation import TranslationService
from backend.services.embedding import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TravelBuddy PC Processing Service",
    description="ML processing service for translation and embedding",
    version="1.0.0"
)

# CORS middleware (allow requests from Pi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Pi's IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy loading - models load on first use)
_translation_service = None
_embedding_service = None


def get_translation_service() -> TranslationService:
    """Get or create translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


# Request/Response models
class TranslateRequest(BaseModel):
    text: str
    source_language: Optional[str] = None


class TranslateResponse(BaseModel):
    translated_text: str
    detected_language: Optional[str] = None


class DetectLanguageRequest(BaseModel):
    text: str


class DetectLanguageResponse(BaseModel):
    language: str
    confidence: Optional[float] = None


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: List[float]


class ProcessBatchRequest(BaseModel):
    texts: List[str]
    source_languages: Optional[List[Optional[str]]] = None


class ProcessBatchItem(BaseModel):
    translated_text: str
    embedding: List[float]
    language: str


class ProcessBatchResponse(BaseModel):
    results: List[ProcessBatchItem]


# API Endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "TravelBuddy PC Processing Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pc_processing"}


@app.post("/detect-language", response_model=DetectLanguageResponse)
def detect_language(request: DetectLanguageRequest):
    """
    Detect the language of the given text.
    
    Uses proper language detection (langdetect library) instead of heuristics.
    """
    try:
        translation_service = get_translation_service()
        detected_lang = translation_service.detect_language(request.text)
        
        return DetectLanguageResponse(
            language=detected_lang,
            confidence=None  # langdetect can provide confidence if needed
        )
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest):
    """
    Translate text to target language (typically English).
    
    If source_language is not provided, it will be auto-detected.
    """
    try:
        translation_service = get_translation_service()
        
        # Detect language if not provided
        detected_lang = None
        if not request.source_language:
            detected_lang = translation_service.detect_language(request.text)
            source_lang = detected_lang
        else:
            source_lang = request.source_language
        
        # Translate
        translated_text = translation_service.translate(
            request.text,
            source_language=source_lang
        )
        
        return TranslateResponse(
            translated_text=translated_text,
            detected_language=detected_lang
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    """
    Generate embedding vector for the given text.
    
    Returns a 384-dimensional vector using miniLM-v6.
    """
    try:
        embedding_service = get_embedding_service()
        embedding_vector = embedding_service.embed(request.text)
        
        return EmbedResponse(embedding=embedding_vector)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-batch", response_model=ProcessBatchResponse)
def process_batch(request: ProcessBatchRequest):
    """
    Process a batch of texts: detect language, translate, and embed.
    
    More efficient than individual requests as models are loaded once.
    """
    try:
        translation_service = get_translation_service()
        embedding_service = get_embedding_service()
        
        results = []
        for i, text in enumerate(request.texts):
            # Detect language
            source_lang = None
            if request.source_languages and i < len(request.source_languages):
                source_lang = request.source_languages[i]
            
            if not source_lang:
                source_lang = translation_service.detect_language(text)
            
            # Translate
            translated_text = translation_service.translate(text, source_language=source_lang)
            
            # Embed
            embedding_vector = embedding_service.embed(translated_text)
            
            results.append(ProcessBatchItem(
                translated_text=translated_text,
                embedding=embedding_vector,
                language=source_lang
            ))
        
        return ProcessBatchResponse(results=results)
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TravelBuddy PC Processing Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    logger.info(f"Starting PC Processing Service on {args.host}:{args.port}")
    uvicorn.run(
        "pc_processing_service:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

