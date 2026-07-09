#!/usr/bin/env python3
"""
Setup script for NLTK data packages needed by the application
"""

import nltk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_nltk():
    """Download required NLTK data packages."""
    required_packages = [
        'vader_lexicon',  # For sentiment analysis
        'punkt',          # For tokenization
        'stopwords'       # Common stopwords
    ]
    
    logger.info("Setting up NLTK data packages...")
    
    for package in required_packages:
        try:
            nltk.data.find(package)
            logger.info(f"Package '{package}' is already downloaded.")
        except LookupError:
            logger.info(f"Downloading package '{package}'...")
            try:
                nltk.download(package, quiet=True)
                logger.info(f"Successfully downloaded package '{package}'.")
            except Exception as e:
                logger.error(f"Failed to download package '{package}': {str(e)}")
    
    logger.info("NLTK setup complete.")

if __name__ == "__main__":
    setup_nltk()