"""
Processing client for communicating with PC-based processing service.

This client runs on the Raspberry Pi and sends processing requests to the PC
via HTTP API. The PC runs the actual ML models (NLLB, miniLM-v6).

Data flow:
1. Pi reads tips from PostgreSQL
2. Pi sends tip text to PC via HTTP API
3. PC processes (translates + embeds) using local models
4. PC returns results to Pi
5. Pi stores results back to PostgreSQL
"""
import logging
import requests
from typing import Optional, Dict, List
from backend.config import settings

logger = logging.getLogger(__name__)


class ProcessingClient:
    """
    Client for communicating with PC-based processing service.
    
    This runs on the Pi and makes HTTP requests to the PC's processing API.
    The PC must have a processing service running that handles translation
    and embedding generation.
    """
    
    def __init__(self, pc_api_url: Optional[str] = None):
        """
        Initialize processing client.
        
        Args:
            pc_api_url: URL of PC's processing API (e.g., http://192.168.1.100:8001)
                       If None, uses settings.pc_ip_address with default port 8001
        """
        if pc_api_url:
            self.api_url = pc_api_url.rstrip('/')
        elif settings.pc_processing_api_url:
            self.api_url = settings.pc_processing_api_url.rstrip('/')
        else:
            # Construct URL from PC IP address
            pc_ip = settings.pc_ip_address
            if not pc_ip:
                raise ValueError("PC IP address not configured in settings")
            self.api_url = f"http://{pc_ip}:{settings.pc_processing_api_port}"
        
        self.timeout = 300  # 5 minutes timeout for processing
    
    def translate(self, text: str, source_language: Optional[str] = None) -> str:
        """
        Translate text using PC's NLLB service.
        
        Args:
            text: Text to translate
            source_language: Source language code (optional, will be detected)
            
        Returns:
            Translated text (in target language, typically English)
        """
        try:
            response = requests.post(
                f"{self.api_url}/translate",
                json={
                    "text": text,
                    "source_language": source_language
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("translated_text", text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Translation request failed: {e}")
            # Return original text on error
            return text
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text using PC's service.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., "en", "es", "fr")
        """
        try:
            response = requests.post(
                f"{self.api_url}/detect-language",
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("language", "en")
        except requests.exceptions.RequestException as e:
            logger.error(f"Language detection request failed: {e}")
            # Fallback to simple heuristic
            return "en"
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding vector using PC's miniLM-v6 service.
        
        Args:
            text: Text to embed
            
        Returns:
            List of 384 float values representing the embedding vector
        """
        try:
            response = requests.post(
                f"{self.api_url}/embed",
                json={"text": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Embedding request failed: {e}")
            raise
    
    def process_batch(
        self,
        texts: List[str],
        source_languages: Optional[List[Optional[str]]] = None
    ) -> List[Dict]:
        """
        Process a batch of texts (translate + embed) in one request.
        
        Args:
            texts: List of texts to process
            source_languages: Optional list of source languages (one per text)
            
        Returns:
            List of dicts with keys: translated_text, embedding, language
        """
        try:
            payload = {"texts": texts}
            if source_languages:
                payload["source_languages"] = source_languages
            
            response = requests.post(
                f"{self.api_url}/process-batch",
                json=payload,
                timeout=self.timeout * len(texts)  # Longer timeout for batches
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Batch processing request failed: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if PC processing service is available.
        
        Returns:
            True if service is reachable, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def get_processing_client() -> ProcessingClient:
    """Get processing client instance"""
    return ProcessingClient()

