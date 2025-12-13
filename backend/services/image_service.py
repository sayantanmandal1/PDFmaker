"""
Image service for searching and downloading images using headless Chrome browser.
"""
import logging
import time
import os
import tempfile
from io import BytesIO
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from PIL import Image
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import settings

logger = logging.getLogger(__name__)


class ImageResult:
    """Represents an image search result."""
    
    def __init__(self, url: str, title: str = "", width: int = 0, height: int = 0, source: str = ""):
        self.url = url
        self.title = title
        self.width = width
        self.height = height
        self.source = source
    
    def __repr__(self):
        return f"ImageResult(url='{self.url}', title='{self.title}', size={self.width}x{self.height})"


class ImageService:
    """Service for searching and downloading images using headless Chrome."""
    
    def __init__(self):
        self.driver = None
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests to avoid rate limiting
    
    def _get_driver(self):
        """Get or create a Chrome WebDriver instance."""
        if self.driver is None:
            try:
                # Setup Chrome options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")  # Don't load images automatically for faster page loads
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Install and setup ChromeDriver
                try:
                    service = Service(ChromeDriverManager().install())
                except Exception as driver_error:
                    logger.error(f"Failed to install ChromeDriver: {driver_error}")
                    raise Exception(f"ChromeDriver installation failed. Please ensure Chrome browser is installed. Error: {driver_error}")
                
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                logger.info("Chrome WebDriver initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Chrome WebDriver: {e}")
                logger.error("Please ensure Google Chrome browser is installed on your system")
                raise Exception(f"Chrome WebDriver initialization failed: {e}")
        
        return self.driver
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_images_google(self, query: str, max_results: int = 5, size_filter: str = "large") -> List[ImageResult]:
        """Search for images using Google Images with headless Chrome."""
        try:
            self._rate_limit()
            driver = self._get_driver()
            
            # Navigate to Google Images
            search_url = f"https://www.google.com/search?q={query}&tbm=isch&hl=en"
            
            # Add size filter for high quality images
            if size_filter == "large":
                search_url += "&tbs=isz:l"  # Large images
            elif size_filter == "medium":
                search_url += "&tbs=isz:m"  # Medium images
            elif size_filter == "icon":
                search_url += "&tbs=isz:i"  # Icon size
            
            logger.info(f"Searching Google Images: {search_url}")
            driver.get(search_url)
            
            # Wait for images to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[data-src], img[src]")))
            
            # Scroll down to load more images
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find image elements
            img_elements = driver.find_elements(By.CSS_SELECTOR, "img[data-src], img[src]")
            
            results = []
            processed_urls = set()
            
            for img_element in img_elements:
                if len(results) >= max_results:
                    break
                
                try:
                    # Get image URL (prefer data-src over src)
                    img_url = img_element.get_attribute("data-src") or img_element.get_attribute("src")
                    
                    if not img_url or img_url in processed_urls:
                        continue
                    
                    # Skip data URLs, SVGs, and very small images
                    if (img_url.startswith("data:") or 
                        img_url.endswith(".svg") or 
                        "1x1" in img_url or
                        "logo" in img_url.lower()):
                        continue
                    
                    # Get image dimensions if available
                    width = 0
                    height = 0
                    try:
                        width = int(img_element.get_attribute("width") or 0)
                        height = int(img_element.get_attribute("height") or 0)
                    except (ValueError, TypeError):
                        pass
                    
                    # Skip very small images
                    if width > 0 and height > 0 and (width < 200 or height < 200):
                        continue
                    
                    # Get alt text as title
                    title = img_element.get_attribute("alt") or ""
                    
                    result = ImageResult(
                        url=img_url,
                        title=title,
                        width=width,
                        height=height,
                        source="google"
                    )
                    
                    results.append(result)
                    processed_urls.add(img_url)
                    
                except Exception as e:
                    logger.debug(f"Error processing image element: {e}")
                    continue
            
            logger.info(f"Successfully found {len(results)} images from Google")
            return results
            
        except Exception as e:
            logger.error(f"Google Images search error: {e}")
            return []
    
    def search_images_with_fallback(self, query: str, max_results: int = 5) -> List[ImageResult]:
        """Search for images with different size filters as fallback."""
        all_results = []
        
        # Try different size filters
        size_filters = ["large", "medium"]
        
        for size_filter in size_filters:
            try:
                logger.info(f"Searching Google Images with {size_filter} size filter")
                results = self.search_images_google(query, max_results, size_filter)
                
                if results:
                    all_results.extend(results)
                    logger.info(f"Found {len(results)} images with {size_filter} filter")
                    
                    # If we have enough results, stop searching
                    if len(all_results) >= max_results:
                        break
                else:
                    logger.warning(f"No results with {size_filter} filter, trying next")
                    
            except Exception as e:
                logger.error(f"Error with {size_filter} filter: {e}")
                continue
        
        if not all_results:
            logger.error(f"All image searches failed for query: {query}")
        
        return all_results[:max_results]
    
    def download_image(self, url: str) -> Optional[bytes]:
        """Download an image using the browser."""
        try:
            self._rate_limit()
            driver = self._get_driver()
            
            # Navigate to the image URL
            driver.get(url)
            
            # Wait for the image to load
            wait = WebDriverWait(driver, 10)
            img_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            
            # Get the image as base64
            canvas_script = """
            var img = arguments[0];
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            canvas.width = img.naturalWidth || img.width;
            canvas.height = img.naturalHeight || img.height;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/jpeg', 0.8);
            """
            
            base64_data = driver.execute_script(canvas_script, img_element)
            
            if base64_data and base64_data.startswith('data:image'):
                # Extract base64 data
                base64_str = base64_data.split(',')[1]
                image_data = base64.b64decode(base64_str)
                
                # Validate the image
                try:
                    with Image.open(BytesIO(image_data)) as img:
                        img.verify()
                    
                    logger.info(f"Successfully downloaded image from {url} ({len(image_data)} bytes)")
                    return image_data
                    
                except Exception as e:
                    logger.warning(f"Downloaded data is not a valid image: {e}")
                    return None
            else:
                logger.warning(f"Failed to get image data from {url}")
                return None
                
        except TimeoutException:
            logger.error(f"Timeout downloading image from {url}")
            return None
        except WebDriverException as e:
            logger.error(f"WebDriver error downloading image from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading image from {url}: {e}")
            return None
    
    def optimize_for_document(self, image_data: bytes, doc_type: str) -> Optional[bytes]:
        """Optimize image for document embedding."""
        try:
            with Image.open(BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Set target dimensions based on document type
                if doc_type == "word":
                    # For Word documents: max 800x600, good for inline images
                    max_width, max_height = 800, 600
                elif doc_type == "powerpoint":
                    # For PowerPoint: max 1200x800, good for slide backgrounds
                    max_width, max_height = 1200, 800
                else:
                    max_width, max_height = 800, 600
                
                # Resize if necessary while maintaining aspect ratio
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save optimized image
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                optimized_data = output.getvalue()
                
                logger.info(f"Optimized image: {len(image_data)} -> {len(optimized_data)} bytes, size: {img.size}")
                return optimized_data
                
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    def determine_image_need(self, content: str) -> bool:
        """Determine if content would benefit from an image."""
        content_lower = content.lower()
        
        # Content that typically benefits from images
        visual_keywords = [
            'portrait', 'photo', 'picture', 'image', 'visual', 'appearance',
            'building', 'architecture', 'landscape', 'scene', 'location',
            'person', 'people', 'individual', 'character', 'figure',
            'artwork', 'painting', 'sculpture', 'design', 'style',
            'historical', 'monument', 'memorial', 'structure', 'place'
        ]
        
        return any(keyword in content_lower for keyword in visual_keywords)
    
    def generate_image_query(self, content: str) -> str:
        """Generate a search query for images based on content."""
        lines = content.split('\n')
        
        # Try to extract key terms from the first few lines
        key_terms = []
        for line in lines[:3]:
            words = line.split()
            # Look for capitalized words (likely proper nouns)
            for word in words:
                if word.istitle() and len(word) > 2:
                    key_terms.append(word)
        
        if key_terms:
            return ' '.join(key_terms[:3])  # Use first 3 key terms
        
        # Fallback: use first few words
        words = content.split()[:5]
        return ' '.join(words)
    
    def determine_placement(self, content: str, doc_type: str) -> str:
        """Determine optimal image placement based on content and document type."""
        if doc_type == "powerpoint":
            # For PowerPoint, decide between background and foreground
            content_lower = content.lower()
            
            # Use background for scenic/atmospheric content
            background_keywords = ['landscape', 'scene', 'background', 'setting', 'atmosphere']
            if any(keyword in content_lower for keyword in background_keywords):
                return "background"
            else:
                return "foreground"
        else:
            # For Word documents, always inline
            return "inline"
    
    def close(self):
        """Close the WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Chrome WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def __del__(self):
        """Cleanup when the service is destroyed."""
        self.close()