"""
Image service for searching, downloading, and processing images.
Implements web scraping with fallback chain: DuckDuckGo -> Bing -> Google.
"""
from typing import List, Optional, Dict, Tuple
import logging
import time
import re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from PIL import Image

from scraping_config import scraping_config

logger = logging.getLogger(__name__)


class ImageResult:
    """Represents an image search result."""
    
    def __init__(self, url: str, thumbnail_url: Optional[str] = None, 
                 title: Optional[str] = None, source: str = "unknown"):
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.title = title
        self.source = source
    
    def __repr__(self):
        return f"ImageResult(url={self.url}, source={self.source})"


class ImageService:
    """Service for image search, download, and processing operations."""
    
    def __init__(self):
        self.config = scraping_config
        self.session = requests.Session()
    
    def search_images(self, query: str, source: str = "wikimedia", 
                     max_results: int = 10) -> List[ImageResult]:
        """
        Search for images using web scraping or APIs.
        
        Args:
            query: Search query string
            source: Image source to use (wikimedia, duckduckgo, bing, google)
            max_results: Maximum number of results to return
            
        Returns:
            List of ImageResult objects
        """
        source = source.lower()
        
        try:
            if source == "wikimedia":
                return self._search_wikimedia(query, max_results)
            elif source == "duckduckgo":
                return self._scrape_duckduckgo(query, max_results)
            elif source == "bing":
                return self._scrape_bing(query, max_results)
            elif source == "google":
                return self._scrape_google(query, max_results)
            else:
                logger.warning(f"Unknown source '{source}', defaulting to Wikimedia")
                return self._search_wikimedia(query, max_results)
        except Exception as e:
            logger.error(f"Error searching images from {source}: {e}")
            return []
    
    def search_images_with_fallback(self, query: str, max_results: int = 10) -> List[ImageResult]:
        """
        Search for images with automatic fallback chain.
        Tries DuckDuckGo -> Bing -> Google until results are found.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ImageResult objects, ranked by relevance
        """
        sources = self.config.get_source_priority()
        
        for source in sources:
            logger.info(f"Attempting to search images from {source}")
            try:
                # Request more results than needed for filtering
                results = self.search_images(query, source, max_results * 2)
                if results:
                    # Rank and filter results
                    ranked_results = self._rank_image_results(results, query)
                    top_results = ranked_results[:max_results]
                    logger.info(f"Successfully found {len(top_results)} images from {source}")
                    return top_results
                else:
                    logger.warning(f"No results from {source}, trying next source")
            except Exception as e:
                logger.error(f"Failed to search {source}: {e}, trying next source")
                continue
        
        logger.error(f"All image sources failed for query: {query}")
        return []
    
    def _rank_image_results(self, results: List[ImageResult], query: str) -> List[ImageResult]:
        """
        Rank image results by relevance and quality indicators.
        
        Args:
            results: List of image results to rank
            query: Original search query
            
        Returns:
            Ranked list of image results
        """
        query_words = set(query.lower().split())
        
        def score_result(result: ImageResult) -> float:
            score = 0.0
            
            # Score based on title relevance
            if result.title:
                title_lower = result.title.lower()
                title_words = set(title_lower.split())
                
                # Boost for query word matches in title
                matches = query_words.intersection(title_words)
                score += len(matches) * 2.0
                
                # Penalize generic titles
                generic_terms = {'image', 'photo', 'picture', 'download', 'free', 'stock'}
                if any(term in title_lower for term in generic_terms):
                    score -= 1.0
            
            # Score based on URL quality
            url_lower = result.url.lower()
            
            # Boost for reputable image sources
            quality_domains = ['wikimedia', 'wikipedia', 'flickr', 'unsplash', 'pexels', 'pixabay']
            if any(domain in url_lower for domain in quality_domains):
                score += 3.0
            
            # Penalize low-quality indicators in URL
            low_quality_indicators = ['thumbnail', 'thumb', 'small', 'icon', 'logo', 'avatar']
            if any(indicator in url_lower for indicator in low_quality_indicators):
                score -= 2.0
            
            # Boost for common high-quality image formats
            if url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
                score += 0.5
            elif url_lower.endswith('.png'):
                score += 0.3
            
            return score
        
        # Score and sort results
        scored_results = [(result, score_result(result)) for result in results]
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        return [result for result, score in scored_results]
    
    def _search_wikimedia(self, query: str, max_results: int) -> List[ImageResult]:
        """
        Search for images from Wikimedia Commons using their official API.
        This is reliable, free, and perfect for educational/historical content.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of ImageResult objects
        """
        config = self.config.get_source_config("wikimedia")
        
        try:
            # Wikimedia requires a proper User-Agent
            headers = {
                "User-Agent": "PDFMaker/1.0 (Educational Document Generator; contact@example.com)"
            }
            
            # Wikimedia Commons API parameters
            params = {
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",  # File namespace
                "gsrlimit": max_results,
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1024",  # Get reasonable size thumbnails
            }
            
            response = self.session.get(
                config["url"],
                params=params,
                headers=headers,
                timeout=config["timeout"]
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract image information from the response
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                imageinfo = page_data.get("imageinfo", [])
                if imageinfo:
                    info = imageinfo[0]
                    image_url = info.get("url")
                    thumbnail_url = info.get("thumburl", image_url)
                    title = page_data.get("title", "").replace("File:", "")
                    
                    # Filter by size and mime type
                    width = info.get("width", 0)
                    height = info.get("height", 0)
                    mime = info.get("mime", "")
                    
                    # Only include reasonably sized images
                    if (width >= 400 and height >= 300 and 
                        mime in ["image/jpeg", "image/png", "image/gif"]):
                        results.append(ImageResult(
                            url=image_url,
                            thumbnail_url=thumbnail_url,
                            title=title,
                            source="wikimedia"
                        ))
                    
                    if len(results) >= max_results:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Wikimedia search error: {e}")
            return []
    
    def _scrape_duckduckgo(self, query: str, max_results: int) -> List[ImageResult]:
        """
        Scrape image results from DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of ImageResult objects
        """
        config = self.config.get_source_config("duckduckgo")
        headers = self.config.get_headers()
        
        try:
            # DuckDuckGo uses a token-based API for images
            # First, get the search page to extract the vqd token
            search_url = "https://duckduckgo.com/"
            params = {"q": query, "iax": "images", "ia": "images"}
            
            response = self.session.get(
                search_url,
                params=params,
                headers=headers,
                timeout=config["timeout"]
            )
            response.raise_for_status()
            
            # Try multiple patterns to extract vqd token
            vqd = None
            
            # Pattern 1: vqd=[\d-]+
            vqd_match = re.search(r'vqd=([\d-]+)', response.text)
            if vqd_match:
                vqd = vqd_match.group(1)
            
            # Pattern 2: "vqd":"value"
            if not vqd:
                vqd_match = re.search(r'"vqd":"([^"]+)"', response.text)
                if vqd_match:
                    vqd = vqd_match.group(1)
            
            # Pattern 3: vqd: "value"
            if not vqd:
                vqd_match = re.search(r'vqd:\s*"([^"]+)"', response.text)
                if vqd_match:
                    vqd = vqd_match.group(1)
            
            if not vqd:
                logger.warning("Could not extract vqd token from DuckDuckGo")
                return []
            
            logger.debug(f"Extracted vqd token: {vqd}")
            
            # Now query the image API
            api_url = "https://duckduckgo.com/i.js"
            api_params = {
                "l": "us-en",
                "o": "json",
                "q": query,
                "vqd": vqd,
                "f": ",,,",
                "p": "1"
            }
            
            time.sleep(self.config.SCRAPING_DELAY)
            
            api_response = self.session.get(
                api_url,
                params=api_params,
                headers=headers,
                timeout=config["timeout"]
            )
            api_response.raise_for_status()
            
            data = api_response.json()
            results = []
            
            for item in data.get("results", [])[:max_results]:
                image_url = item.get("image")
                thumbnail_url = item.get("thumbnail")
                title = item.get("title", "")
                
                if image_url and self._is_valid_image_url(image_url):
                    results.append(ImageResult(
                        url=image_url,
                        thumbnail_url=thumbnail_url,
                        title=title,
                        source="duckduckgo"
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo scraping error: {e}")
            return []
    
    def _scrape_bing(self, query: str, max_results: int) -> List[ImageResult]:
        """
        Scrape image results from Bing Images.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of ImageResult objects
        """
        config = self.config.get_source_config("bing")
        headers = self.config.get_headers()
        
        url = config["url"]
        params = {
            config["search_param"]: query,
            "first": "1",
            "count": str(max_results * 2),  # Request more to filter
            "qft": "+filterui:photo-photo",  # Filter for photos
        }
        params.update(config["image_params"])
        
        try:
            time.sleep(self.config.SCRAPING_DELAY)
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=config["timeout"]
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Bing stores image data in m attribute of anchor tags
            image_links = soup.find_all('a', class_='iusc')
            
            for link in image_links:
                if len(results) >= max_results:
                    break
                    
                m_attr = link.get('m')
                if m_attr:
                    try:
                        import json
                        data = json.loads(m_attr)
                        image_url = data.get('murl')  # Use murl (full size) not turl (thumbnail)
                        thumbnail_url = data.get('turl')
                        title = data.get('t', '')
                        
                        # Validate and filter images
                        if image_url and self._is_valid_image_url(image_url):
                            # Skip very small images (likely icons/logos)
                            width = data.get('w', 0)
                            height = data.get('h', 0)
                            if width >= 400 and height >= 300:  # Minimum size filter
                                results.append(ImageResult(
                                    url=image_url,
                                    thumbnail_url=thumbnail_url,
                                    title=title,
                                    source="bing"
                                ))
                    except Exception as e:
                        logger.debug(f"Error parsing Bing image data: {e}")
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Bing scraping error: {e}")
            return []
    
    def _scrape_google(self, query: str, max_results: int) -> List[ImageResult]:
        """
        Scrape image results from Google Images.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of ImageResult objects
        """
        config = self.config.get_source_config("google")
        headers = self.config.get_headers()
        
        url = config["url"]
        params = {
            config["search_param"]: query,
            "tbm": "isch",
            "tbs": "isz:l"  # Large images only
        }
        params.update(config["image_params"])
        
        try:
            time.sleep(self.config.SCRAPING_DELAY)
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=config["timeout"]
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Try to extract from script tags containing image data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('AF_initDataCallback' in script.string or 'data:' in script.string):
                    # Extract URLs using regex - look for actual image URLs
                    urls = re.findall(r'https?://[^"\'\\]+\.(?:jpg|jpeg|png|gif|webp)', script.string)
                    for url in urls:
                        if len(results) >= max_results:
                            break
                        # Filter out Google's own images and tracking pixels
                        if self._is_valid_image_url(url) and 'google.com' not in url:
                            results.append(ImageResult(
                                url=url,
                                thumbnail_url=url,
                                title="",
                                source="google"
                            ))
                    
                    if len(results) >= max_results:
                        break
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Google scraping error: {e}")
            return []
    
    def _is_valid_image_url(self, url: str) -> bool:
        """
        Validate if a URL is likely a valid image URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears valid, False otherwise
        """
        if not url or not url.startswith('http'):
            return False
        
        # Filter out common non-image patterns
        invalid_patterns = [
            'data:image',  # Data URLs
            'base64',
            'logo',  # Often small logos
            'icon',
            'avatar',
            'thumbnail',
            'pixel',  # Tracking pixels
            '1x1',
            'spacer',
            'blank',
        ]
        
        url_lower = url.lower()
        for pattern in invalid_patterns:
            if pattern in url_lower:
                return False
        
        # Check for valid image extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        has_valid_ext = any(ext in url_lower for ext in valid_extensions)
        
        return has_valid_ext
    
    def download_image(self, url: str, timeout: Optional[int] = None) -> Optional[bytes]:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            timeout: Optional timeout in seconds
            
        Returns:
            Image data as bytes, or None if download fails
        """
        if timeout is None:
            timeout = self.config.DOWNLOAD_TIMEOUT
        
        headers = self.config.get_headers()
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > self.config.MAX_FILE_SIZE_MB:
                    logger.warning(f"Image too large: {size_mb:.2f}MB (max: {self.config.MAX_FILE_SIZE_MB}MB)")
                    return None
            
            # Download the image
            image_data = response.content
            
            # Validate it's actually an image
            try:
                Image.open(BytesIO(image_data))
            except Exception as e:
                logger.warning(f"Downloaded data is not a valid image: {e}")
                return None
            
            return image_data
            
        except requests.Timeout:
            logger.error(f"Timeout downloading image from {url}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading image: {e}")
            return None
    
    def resize_image(self, image_bytes: bytes, max_width: int, max_height: int) -> Optional[bytes]:
        """
        Resize image to fit within specified dimensions while maintaining aspect ratio.
        
        Args:
            image_bytes: Image data as bytes
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            
        Returns:
            Resized image data as bytes, or None if resize fails
        """
        try:
            # Open the image
            image = Image.open(BytesIO(image_bytes))
            
            # Get original dimensions
            original_width, original_height = image.size
            
            # Check if resize is needed
            if original_width <= max_width and original_height <= max_height:
                logger.debug(f"Image already within bounds ({original_width}x{original_height})")
                return image_bytes
            
            # Calculate new dimensions maintaining aspect ratio
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            resize_ratio = min(width_ratio, height_ratio)
            
            new_width = int(original_width * resize_ratio)
            new_height = int(original_height * resize_ratio)
            
            logger.info(f"Resizing image from {original_width}x{original_height} to {new_width}x{new_height}")
            
            # Resize the image using high-quality resampling
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = BytesIO()
            
            # Preserve format or default to JPEG
            format_to_use = image.format if image.format else 'JPEG'
            
            # Convert RGBA to RGB for JPEG
            if format_to_use == 'JPEG' and resized_image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                rgb_image = Image.new('RGB', resized_image.size, (255, 255, 255))
                if resized_image.mode == 'P':
                    resized_image = resized_image.convert('RGBA')
                rgb_image.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode == 'RGBA' else None)
                resized_image = rgb_image
            
            resized_image.save(output, format=format_to_use, quality=85)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return None
    
    def optimize_for_document(self, image_bytes: bytes, doc_type: str) -> Optional[bytes]:
        """
        Optimize image for document embedding with appropriate compression and sizing.
        
        Args:
            image_bytes: Image data as bytes
            doc_type: Document type ('powerpoint' or 'word')
            
        Returns:
            Optimized image data as bytes, or None if optimization fails
        """
        try:
            # Open the image
            image = Image.open(BytesIO(image_bytes))
            original_format = image.format
            
            # Define size limits based on document type
            if doc_type.lower() == 'powerpoint':
                # PowerPoint: optimize for slides (1920x1080 max for backgrounds)
                max_width = 1920
                max_height = 1080
                quality = 85
            elif doc_type.lower() == 'word':
                # Word: optimize for page width (6.5 inches at 150 DPI)
                max_width = 975  # 6.5 inches * 150 DPI
                max_height = 1500  # Reasonable max height
                quality = 90
            else:
                logger.warning(f"Unknown document type '{doc_type}', using default settings")
                max_width = 1920
                max_height = 1080
                quality = 85
            
            # Resize if needed
            resized_bytes = self.resize_image(image_bytes, max_width, max_height)
            if resized_bytes is None:
                logger.error("Failed to resize image during optimization")
                return None
            
            # Re-open the resized image for further optimization
            image = Image.open(BytesIO(resized_bytes))
            
            # Optimize and compress
            output = BytesIO()
            
            # Determine output format
            if original_format in ['JPEG', 'JPG']:
                format_to_use = 'JPEG'
            elif original_format == 'PNG':
                # Keep PNG for images with transparency
                if image.mode in ('RGBA', 'LA'):
                    format_to_use = 'PNG'
                else:
                    # Convert to JPEG for better compression
                    format_to_use = 'JPEG'
            else:
                # Default to JPEG for other formats
                format_to_use = 'JPEG'
            
            # Convert mode if necessary
            if format_to_use == 'JPEG':
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for JPEG
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    if image.mode in ('RGBA', 'LA'):
                        rgb_image.paste(image, mask=image.split()[-1])
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
            
            # Save with optimization
            if format_to_use == 'JPEG':
                image.save(output, format='JPEG', quality=quality, optimize=True)
            else:
                image.save(output, format='PNG', optimize=True)
            
            optimized_bytes = output.getvalue()
            
            # Log size reduction
            original_size = len(image_bytes) / 1024  # KB
            optimized_size = len(optimized_bytes) / 1024  # KB
            reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
            
            logger.info(f"Optimized image for {doc_type}: {original_size:.1f}KB -> {optimized_size:.1f}KB ({reduction:.1f}% reduction)")
            
            return optimized_bytes
            
        except Exception as e:
            logger.error(f"Error optimizing image for document: {e}")
            return None
    
    def close(self):
        """Close the requests session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
