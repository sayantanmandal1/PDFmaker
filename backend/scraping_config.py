"""
Web scraping configuration for image search and retrieval.
Includes user-agent rotation, timeout settings, and retry logic.
"""
from typing import List, Dict
import random


class ScrapingConfig:
    """Configuration for web scraping operations."""
    
    # User-Agent rotation list to avoid blocking
    USER_AGENTS: List[str] = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    ]
    
    # Image source priority chain
    IMAGE_SOURCES: List[str] = [
        "wikimedia",
        "duckduckgo",
        "bing",
        "google"
    ]
    
    # Source-specific configurations
    SOURCE_CONFIGS: Dict[str, Dict] = {
        "wikimedia": {
            "url": "https://commons.wikimedia.org/w/api.php",
            "search_param": "gsrsearch",
            "timeout": 10,
            "max_results": 10,
        },
        "duckduckgo": {
            "url": "https://duckduckgo.com/",
            "search_param": "q",
            "image_params": {"iax": "images", "ia": "images"},
            "timeout": 10,
            "max_results": 10,
        },
        "bing": {
            "url": "https://www.bing.com/images/search",
            "search_param": "q",
            "image_params": {},
            "timeout": 10,
            "max_results": 10,
        },
        "google": {
            "url": "https://www.google.com/search",
            "search_param": "q",
            "image_params": {"tbm": "isch"},
            "timeout": 10,
            "max_results": 10,
        }
    }
    
    # Request settings
    REQUEST_TIMEOUT: int = 10
    DOWNLOAD_TIMEOUT: int = 15
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # seconds
    SCRAPING_DELAY: float = 1.0  # seconds between requests
    
    # Image constraints
    MAX_FILE_SIZE_MB: int = 5
    MAX_IMAGE_WIDTH: int = 1920
    MAX_IMAGE_HEIGHT: int = 1080
    
    # Supported image formats
    SUPPORTED_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get a random user-agent from the rotation list."""
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def get_headers(cls, custom_user_agent: str = None) -> Dict[str, str]:
        """
        Get HTTP headers for scraping requests.
        
        Args:
            custom_user_agent: Optional custom user-agent string
            
        Returns:
            Dictionary of HTTP headers
        """
        user_agent = custom_user_agent or cls.get_random_user_agent()
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
    
    @classmethod
    def get_source_config(cls, source: str) -> Dict:
        """
        Get configuration for a specific image source.
        
        Args:
            source: Image source name (duckduckgo, bing, google)
            
        Returns:
            Configuration dictionary for the source
        """
        return cls.SOURCE_CONFIGS.get(source.lower(), cls.SOURCE_CONFIGS["duckduckgo"])
    
    @classmethod
    def get_source_priority(cls) -> List[str]:
        """
        Get the priority order for image sources.
        
        Returns:
            List of source names in priority order
        """
        return cls.IMAGE_SOURCES.copy()


# Global scraping configuration instance
scraping_config = ScrapingConfig()
