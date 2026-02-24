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
import threading
from contextlib import asynccontextmanager
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import services
# Note: These need to be imported from the backend package
# Make sure the backend directory is in Python path or install as package
import sys
import os
import subprocess
import git

repo = git.Repo(os.path.dirname(os.path.abspath(__file__)))

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

_translation_service: Optional[TranslationService] = None
_embedding_service: Optional[EmbeddingService] = None

RESTART_CODE="75"

def get_translation_service() -> TranslationService:
    return _translation_service


def get_embedding_service() -> EmbeddingService:
    return _embedding_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models at startup so workers are ready before accepting requests."""
    global _translation_service, _embedding_service
    logger.info("Loading models at startup...")
    _translation_service = TranslationService()
    _translation_service._load_model()
    _embedding_service = EmbeddingService()
    _embedding_service._load_model()
    logger.info("Models loaded, ready to serve requests")
    yield


# Create FastAPI app
app = FastAPI(
    title="TravelBuddy PC Processing Service",
    description="ML processing service for translation and embedding",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (allow requests from Pi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Pi's IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class TranslateRequest(BaseModel):
    text: str
    source_language: Optional[str] = None


class TranslateResponse(BaseModel):
    translated_text: str
    detected_language: Optional[str] = None


class TranslateMultiRequest(BaseModel):
    text: str
    source_language: str
    target_languages: List[str]


class TranslateMultiResponse(BaseModel):
    translations: Dict[str, str]


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


class TranslateMultiBatchRequest(BaseModel):
    texts: List[str]
    source_language: str
    target_languages: List[str]


class TranslateMultiBatchResponse(BaseModel):
    # translations[lang_code] = list of translated texts, same order as input texts
    translations: Dict[str, List[str]]


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


@app.post("/translate-multi", response_model=TranslateMultiResponse)
def translate_to_multiple_languages(request: TranslateMultiRequest):
    """
    Translate text to multiple target languages in one request.

    Used for translating promoted tips to all supported languages.
    More efficient than making multiple individual translation requests.
    """
    try:
        translation_service = get_translation_service()
        translations = translation_service.translate_to_multiple_languages(
            request.text,
            request.source_language,
            request.target_languages
        )
        return TranslateMultiResponse(translations=translations)
    except Exception as e:
        logger.error(f"Multi-language translation error: {e}")
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

    Groups texts by source language so each language gets a single batched
    model.generate() call, then embeds all translated texts in one shot.
    """
    try:
        translation_service = get_translation_service()
        embedding_service = get_embedding_service()

        texts = request.texts
        n = len(texts)

        # Detect languages for all texts
        detected_langs = []
        for i, text in enumerate(texts):
            if request.source_languages and i < len(request.source_languages) and request.source_languages[i]:
                detected_langs.append(request.source_languages[i])
            else:
                detected_langs.append(translation_service.detect_language(text))

        # Group texts by source language for batch translation
        from collections import defaultdict
        lang_groups: dict = defaultdict(list)  # lang -> [(original_idx, text)]
        for i, (text, lang) in enumerate(zip(texts, detected_langs)):
            lang_groups[lang].append((i, text))

        translated_texts = [None] * n

        # One batched translate call per unique source language
        for lang, group in lang_groups.items():
            indices = [g[0] for g in group]
            group_texts = [g[1] for g in group]
            translated = translation_service.translate_batch(group_texts, source_language=lang)
            for idx, trans in zip(indices, translated):
                translated_texts[idx] = trans

        # Embed all translated texts in a single batch call
        embeddings = embedding_service.embed_batch(translated_texts)

        results = [
            ProcessBatchItem(
                translated_text=translated_texts[i],
                embedding=embeddings[i],
                language=detected_langs[i],
            )
            for i in range(n)
        ]

        return ProcessBatchResponse(results=results)
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate-multi-batch", response_model=TranslateMultiBatchResponse)
def translate_to_multiple_languages_batch(request: TranslateMultiBatchRequest):
    """
    Translate a batch of texts to multiple target languages.

    Replaces N concurrent translate-multi calls with a single request.
    For each target language, all texts are translated in one batched
    model.generate() call — reducing M*N generate() calls to just M calls
    (one per target language).
    """
    try:
        translation_service = get_translation_service()
        translations: Dict[str, List[str]] = {}

        # Always include source language texts as-is
        translations[request.source_language] = list(request.texts)

        for target_lang in request.target_languages:
            if target_lang == request.source_language:
                continue
            translations[target_lang] = translation_service.translate_batch_to_language(
                request.texts, request.source_language, target_lang
            )

        return TranslateMultiBatchResponse(translations=translations)
    except Exception as e:
        logger.error(f"Multi-batch translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/git-update")
def git_update():
    """
    Update the PC from the git repository.
    """
    try:
        repo.remotes.origin.pull()
        return {"status": "git update successful"}
    except Exception as e:
        logger.error(f"Git update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        def close():
            sys.exit(RESTART_CODE)
        threading.Timer(1.0, close).start()


@app.post("/shutdown")
def shutdown():
    """
    Shutdown the PC.
    """
    try:
        subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        return {"status": "shutdown initiated"}
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/logs")
def get_logs():
    """
    Get the logs of the PC.
    """
    try:
        with open(f"{repo.working_dir}/wol_run.log", "r") as f:
            return {"logs": f.read()}
    except Exception as e:
        logger.error(f"Logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TravelBuddy PC Processing Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes (default: 4)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (disables workers)")

    args = parser.parse_args()

    # Note: --reload and --workers are mutually exclusive
    # When --reload is enabled, workers are automatically set to 1
    if args.reload:
        logger.info(f"Starting PC Processing Service on {args.host}:{args.port} with auto-reload (single worker)")
        uvicorn.run(
            "pc_processing_service:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    else:
        logger.info(f"Starting PC Processing Service on {args.host}:{args.port} with {args.workers} workers")
        uvicorn.run(
            "pc_processing_service:app",
            host=args.host,
            port=args.port,
            workers=args.workers
        )

