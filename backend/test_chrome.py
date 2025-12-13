#!/usr/bin/env python3
"""
Test script to verify Chrome WebDriver installation and basic functionality.
"""
import logging
from services.image_service import ImageService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chrome_setup():
    """Test Chrome WebDriver setup."""
    try:
        logger.info("Testing Chrome WebDriver setup...")
        
        # Initialize image service
        image_service = ImageService()
        
        # Test basic search
        logger.info("Testing image search...")
        results = image_service.search_images_google("test image", max_results=2)
        
        logger.info(f"Found {len(results)} images")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result.url}")
        
        # Test image download if we have results
        if results:
            logger.info("Testing image download...")
            image_data = image_service.download_image(results[0].url)
            if image_data:
                logger.info(f"Successfully downloaded image ({len(image_data)} bytes)")
            else:
                logger.warning("Failed to download image")
        
        # Cleanup
        image_service.close()
        logger.info("Chrome WebDriver test completed successfully!")
        
    except Exception as e:
        logger.error(f"Chrome WebDriver test failed: {e}")
        raise

if __name__ == "__main__":
    test_chrome_setup()