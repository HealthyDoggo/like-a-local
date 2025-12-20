"""NLLB translation service"""
import logging
from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from backend.config import settings

logger = logging.getLogger(__name__)

# Language code mapping for common languages
LANGUAGE_CODES = {
    "en": "eng_Latn",
    "es": "spa_Latn",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "ko": "kor_Hang",
    "zh": "zho_Hans",
    "ar": "arb_Arab",
    "hi": "hin_Deva",
    "th": "tha_Thai",
    "vi": "vie_Latn",
    "id": "ind_Latn",
}


class TranslationService:
    """NLLB translation service"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.target_language = settings.target_language
        self._model_loaded = False
    
    def _load_model(self):
        """Lazy load the translation model"""
        if self._model_loaded:
            return
        
        try:
            logger.info(f"Loading NLLB model: {settings.nllb_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.nllb_model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.nllb_model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model.to(self.device)
            self.model.eval()
            self._model_loaded = True
            logger.info(f"NLLB model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load NLLB model: {e}")
            raise
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language of text (simplified - returns ISO code)"""
        # Simple heuristic: check for common language patterns
        # In production, use a proper language detection library like langdetect
        text_lower = text.lower()
        
        # Check for common words/patterns
        if any(word in text_lower for word in ["the", "and", "is", "are", "was", "were"]):
            return "en"
        elif any(word in text_lower for word in ["el", "la", "de", "que", "y", "es"]):
            return "es"
        elif any(word in text_lower for word in ["le", "de", "et", "est", "un", "une"]):
            return "fr"
        elif any(word in text_lower for word in ["der", "die", "das", "und", "ist", "sind"]):
            return "de"
        elif any(word in text_lower for word in ["il", "la", "di", "e", "è", "un", "una"]):
            return "it"
        
        # Default to English if uncertain
        return "en"
    
    def translate(self, text: str, source_language: Optional[str] = None) -> str:
        """Translate text to target language"""
        if not text or not text.strip():
            return text
        
        self._load_model()
        
        # Detect language if not provided
        if not source_language:
            source_language = self.detect_language(text)
        
        # Convert ISO code to NLLB code
        source_lang_code = LANGUAGE_CODES.get(source_language, "eng_Latn")
        
        # If already in target language, return as-is
        if source_lang_code == self.target_language:
            return text
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Translate
            with torch.no_grad():
                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[self.target_language],
                    max_length=512
                )
            
            # Decode
            translated_text = self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0]
            
            return translated_text
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            # Return original text on error
            return text
    
    def translate_batch(self, texts: List[str], source_language: Optional[str] = None) -> List[str]:
        """Translate a batch of texts"""
        if not texts:
            return []
        
        self._load_model()
        
        # Detect language if not provided
        if not source_language:
            source_language = self.detect_language(texts[0])
        
        # Convert ISO code to NLLB code
        source_lang_code = LANGUAGE_CODES.get(source_language, "eng_Latn")
        
        # If already in target language, return as-is
        if source_lang_code == self.target_language:
            return texts
        
        try:
            # Tokenize batch
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Translate
            with torch.no_grad():
                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[self.target_language],
                    max_length=512
                )
            
            # Decode
            translated_texts = self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )
            
            return translated_texts
        
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            # Return original texts on error
            return texts


# Global instance
_translation_service = None


def get_translation_service() -> TranslationService:
    """Get or create translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service

