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
import requests

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
                # Setup Chrome options to avoid detection
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")  # Use new headless mode
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument("--disable-background-timer-throttling")
                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                chrome_options.add_argument("--disable-renderer-backgrounding")
                chrome_options.add_argument("--disable-features=TranslateUI")
                chrome_options.add_argument("--disable-ipc-flooding-protection")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--no-default-browser-check")
                chrome_options.add_argument("--no-pings")
                chrome_options.add_argument("--password-store=basic")
                chrome_options.add_argument("--use-mock-keychain")
                
                # Realistic user agent
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Disable automation indicators
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Add preferences to appear more human-like
                prefs = {
                    "profile.default_content_setting_values": {
                        "notifications": 2,
                        "geolocation": 2,
                    },
                    "profile.managed_default_content_settings": {
                        "images": 1  # Allow images
                    }
                }
                chrome_options.add_experimental_option("prefs", prefs)
                
                # Install and setup ChromeDriver
                try:
                    driver_path = ChromeDriverManager().install()
                    
                    # Fix for WebDriver Manager bug - ensure we get the actual executable
                    if not driver_path.endswith('chromedriver.exe'):
                        # Look for chromedriver.exe in the same directory
                        import os
                        driver_dir = os.path.dirname(driver_path)
                        potential_exe = os.path.join(driver_dir, 'chromedriver.exe')
                        if os.path.exists(potential_exe):
                            driver_path = potential_exe
                        else:
                            # Look in subdirectories
                            for root, dirs, files in os.walk(driver_dir):
                                if 'chromedriver.exe' in files:
                                    driver_path = os.path.join(root, 'chromedriver.exe')
                                    break
                    
                    logger.info(f"Using ChromeDriver at: {driver_path}")
                    service = Service(driver_path)
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
            
            # Use the most reliable Google Images URL
            search_url = f"https://www.google.com/search?q={query}&tbm=isch&hl=en&safe=off"
            
            # Add size filter for high quality images
            if size_filter == "large":
                search_url += "&tbs=isz:l"  # Large images
            elif size_filter == "medium":
                search_url += "&tbs=isz:m"  # Medium images
            
            logger.info(f"Searching Google Images: {search_url}")
            driver.get(search_url)
            
            # Wait for page to load completely
            time.sleep(5)
            
            # Check if we got blocked
            page_title = driver.title
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            if ("sorry" in current_url.lower() or 
                "blocked" in page_title.lower() or
                "unusual traffic" in page_source or
                "captcha" in page_source):
                logger.warning("Detected blocking by Google, trying alternative approach")
                # Try to bypass by clicking through
                try:
                    # Look for "I'm not a robot" or continue buttons
                    continue_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
                    if continue_buttons:
                        continue_buttons[0].click()
                        time.sleep(3)
                except:
                    pass
            
            # Scroll down to load more images first
            logger.info("Scrolling to load more images...")
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Look for image elements with comprehensive approach
            logger.info("Looking for image elements...")
            
            # Try to find clickable image containers first
            clickable_selectors = [
                "div[data-tbnid]",
                "a[jsname]",
                ".rg_bx",
                ".isv-r"
            ]
            
            clickable_elements = []
            for selector in clickable_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                clickable_elements.extend(elements)
                if elements:
                    logger.info(f"Found {len(elements)} clickable elements with selector: {selector}")
            
            results = []
            processed_urls = set()
            
            # Try clicking on image containers to get high-res images
            for i, element in enumerate(clickable_elements[:max_results * 2]):
                if len(results) >= max_results:
                    break
                
                try:
                    # Click on the element
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    
                    # Look for the high-resolution image that appears
                    high_res_selectors = [
                        "img[src*='http']:not([src*='gstatic']):not([src*='data:'])",
                        ".n3VNCb",  # Google's high-res image class
                        ".iPVvYb",  # Another Google image class
                        ".r48jcc"   # Yet another class
                    ]
                    
                    for hr_selector in high_res_selectors:
                        hr_images = driver.find_elements(By.CSS_SELECTOR, hr_selector)
                        for hr_img in hr_images:
                            img_url = hr_img.get_attribute("src")
                            if (img_url and 
                                img_url not in processed_urls and
                                not img_url.startswith("data:") and
                                "gstatic" not in img_url and
                                any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])):
                                
                                # Get image details
                                title = hr_img.get_attribute("alt") or f"Google image for {query}"
                                width = int(hr_img.get_attribute("naturalWidth") or hr_img.get_attribute("width") or 0)
                                height = int(hr_img.get_attribute("naturalHeight") or hr_img.get_attribute("height") or 0)
                                
                                result = ImageResult(
                                    url=img_url,
                                    title=title,
                                    width=width,
                                    height=height,
                                    source="google"
                                )
                                
                                results.append(result)
                                processed_urls.add(img_url)
                                logger.info(f"Found high-res Google image: {img_url[:60]}...")
                                break
                    
                    # Close the opened image view
                    driver.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
                    time.sleep(1)
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception as click_error:
                    logger.debug(f"Could not process clickable element {i}: {click_error}")
                    continue
            
            if results:
                logger.info(f"Successfully found {len(results)} images from Google")
                return results
            
            # Fallback: try to get images directly without clicking
            logger.info("Trying fallback direct image extraction...")
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            
            results = []
            processed_urls = set()
            
            for img_element in img_elements:
                if len(results) >= max_results:
                    break
                
                try:
                    # Try multiple ways to get the image URL
                    img_url = None
                    
                    # Method 1: Check various data attributes
                    for attr in ["data-src", "src", "data-iurl", "data-original", "data-deferred"]:
                        url = img_element.get_attribute(attr)
                        if url and not url.startswith("data:"):
                            img_url = url
                            break
                    
                    # Method 2: Try to click on the image to get high-res version
                    if not img_url or "gstatic" in img_url:
                        try:
                            # Click on the image to open it
                            driver.execute_script("arguments[0].click();", img_element)
                            time.sleep(2)
                            
                            # Look for the high-res image in the opened view
                            high_res_imgs = driver.find_elements(By.CSS_SELECTOR, "img[src*='http']:not([src*='gstatic'])")
                            for hr_img in high_res_imgs:
                                hr_url = hr_img.get_attribute("src")
                                if hr_url and any(ext in hr_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                    img_url = hr_url
                                    break
                            
                            # Close the opened view by pressing Escape
                            driver.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
                            time.sleep(1)
                            
                        except Exception as click_error:
                            logger.debug(f"Could not click image: {click_error}")
                    
                    if not img_url or img_url in processed_urls:
                        continue
                    
                    # Skip unwanted image types
                    skip_patterns = [
                        "data:", ".svg", "1x1", "logo", "icon", "button", 
                        "transparent", "spacer", "pixel", "blank", "avatar",
                        "profile", "thumbnail"
                    ]
                    
                    if any(pattern in img_url.lower() for pattern in skip_patterns):
                        continue
                    
                    # Only accept proper image URLs
                    valid_patterns = ['.jpg', '.jpeg', '.png', '.webp', 'images', 'media', 'photo']
                    if not any(pattern in img_url.lower() for pattern in valid_patterns):
                        continue
                    
                    # Skip very small images based on URL patterns
                    if any(size in img_url for size in ['=s64', '=s96', '=s128', 'w=64', 'h=64']):
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
    
    def search_images_pinterest(self, query: str, max_results: int = 5) -> List[ImageResult]:
        """Search for images using Pinterest with headless Chrome."""
        try:
            self._rate_limit()
            driver = self._get_driver()
            
            # Pinterest search URL
            search_url = f"https://www.pinterest.com/search/pins/?q={query}"
            
            logger.info(f"Searching Pinterest: {search_url}")
            driver.get(search_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Scroll to load more pins
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find Pinterest pin images
            pin_selectors = [
                "img[src*='pinimg.com']",
                "div[data-test-id='pin'] img",
                ".Yl- img",  # Pinterest pin container
                ".GrowthUnauthPinImage img"
            ]
            
            img_elements = []
            for selector in pin_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                img_elements.extend(elements)
                if elements:
                    logger.info(f"Found {len(elements)} images with Pinterest selector: {selector}")
            
            results = []
            processed_urls = set()
            
            for img_element in img_elements:
                if len(results) >= max_results:
                    break
                
                try:
                    img_url = img_element.get_attribute("src")
                    
                    if not img_url or img_url in processed_urls:
                        continue
                    
                    # Convert small Pinterest thumbnails to larger versions
                    if 'pinimg.com' in img_url:
                        # Replace small sizes with larger ones
                        size_replacements = {
                            '60x60': '736x',
                            '236x': '736x', 
                            '474x': '736x',
                            '75x75': '736x',
                            '170x': '736x',
                            '564x': '736x'
                        }
                        
                        for small_size, large_size in size_replacements.items():
                            if small_size in img_url:
                                img_url = img_url.replace(small_size, large_size)
                                break
                        
                        # If no size found, try to add 736x
                        if '/60x60/' in img_url:
                            img_url = img_url.replace('/60x60/', '/736x/')
                        elif not any(size in img_url for size in ['736x', '564x', '474x']):
                            # Insert 736x before the filename
                            parts = img_url.split('/')
                            if len(parts) > 3:
                                parts.insert(-1, '736x')
                                img_url = '/'.join(parts)
                    
                    # Get alt text as title
                    title = img_element.get_attribute("alt") or f"Pinterest image for {query}"
                    
                    # Get dimensions if available
                    width = 0
                    height = 0
                    try:
                        width = int(img_element.get_attribute("width") or 0)
                        height = int(img_element.get_attribute("height") or 0)
                    except (ValueError, TypeError):
                        pass
                    
                    result = ImageResult(
                        url=img_url,
                        title=title,
                        width=width,
                        height=height,
                        source="pinterest"
                    )
                    
                    results.append(result)
                    processed_urls.add(img_url)
                    
                except Exception as e:
                    logger.debug(f"Error processing Pinterest image: {e}")
                    continue
            
            logger.info(f"Successfully found {len(results)} images from Pinterest")
            return results
            
        except Exception as e:
            logger.error(f"Pinterest search error: {e}")
            return []
    
    def search_images_placeholder(self, query: str, max_results: int = 5) -> List[ImageResult]:
        """Generate placeholder images for development/fallback."""
        try:
            results = []
            
            # Create placeholder images with different sizes
            sizes = [(800, 600), (1024, 768), (640, 480)]
            
            for i in range(min(max_results, len(sizes))):
                width, height = sizes[i]
                
                # Use a placeholder service that doesn't require API keys
                placeholder_url = f"https://picsum.photos/{width}/{height}?random={hash(query + str(i)) % 1000}"
                
                result = ImageResult(
                    url=placeholder_url,
                    title=f"Placeholder image for {query}",
                    width=width,
                    height=height,
                    source="placeholder"
                )
                
                results.append(result)
            
            logger.info(f"Generated {len(results)} placeholder images")
            return results
            
        except Exception as e:
            logger.error(f"Placeholder image generation error: {e}")
            return []

    def search_images_with_fallback(self, query: str, max_results: int = 5) -> List[ImageResult]:
        """Search for images with multiple real sources as fallback."""
        all_results = []
        
        # Try Pinterest first (often less restrictive)
        try:
            logger.info("Searching Pinterest for images")
            pinterest_results = self.search_images_pinterest(query, max_results)
            if pinterest_results:
                all_results.extend(pinterest_results)
                logger.info(f"Found {len(pinterest_results)} images from Pinterest")
                
                # If we have enough results, return them
                if len(all_results) >= max_results:
                    return all_results[:max_results]
        except Exception as e:
            logger.error(f"Pinterest search failed: {e}")
        
        # If Pinterest didn't provide enough results, try Google Images
        remaining_needed = max_results - len(all_results)
        if remaining_needed > 0:
            # Try different size filters with improved scraping
            size_filters = ["large", "medium"]
            
            for size_filter in size_filters:
                try:
                    logger.info(f"Searching Google Images with {size_filter} size filter")
                    results = self.search_images_google(query, remaining_needed, size_filter)
                    
                    if results:
                        all_results.extend(results)
                        logger.info(f"Found {len(results)} images from Google with {size_filter} filter")
                        
                        # If we have enough results, stop searching
                        if len(all_results) >= max_results:
                            break
                    else:
                        logger.warning(f"No results with {size_filter} filter, trying next")
                        
                except Exception as e:
                    logger.error(f"Error with Google {size_filter} filter: {e}")
                    continue
        
        # Only use placeholders if absolutely no real images were found
        if not all_results:
            logger.error(f"FAILED to find any real images for query: {query}")
            logger.error("This should not happen - please check the scraping logic")
            # Don't use placeholders - return empty list to force debugging
            return []
        
        logger.info(f"Successfully found {len(all_results)} real images for query: {query}")
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