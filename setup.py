#!/usr/bin/env python3
"""
Setup script for Advanced NER Project
This script installs dependencies and downloads required spaCy models
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {command}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    return run_command(f"{sys.executable} -m pip install -r requirements.txt")

def download_spacy_models():
    """Download spaCy language models"""
    models = [
        'en_core_web_sm',  # English
        'es_core_news_sm', # Spanish
        'fr_core_news_sm', # French
        'de_core_news_sm', # German
        'it_core_news_sm', # Italian
        'pt_core_news_sm', # Portuguese
        'nl_core_news_sm', # Dutch
    ]
    
    print("Downloading spaCy models...")
    success_count = 0
    
    for model in models:
        print(f"\nDownloading {model}...")
        if run_command(f"{sys.executable} -m spacy download {model}"):
            success_count += 1
        else:
            print(f"Failed to download {model} - continuing with others...")
    
    print(f"\nSuccessfully downloaded {success_count}/{len(models)} models")
    return success_count > 0

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'models',
        'outputs',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Advanced NER Project Setup")
    print("=" * 60)
    
    # Create directories
    print("\n1. Creating project directories...")
    create_directories()
    
    # Install requirements
    print("\n2. Installing Python requirements...")
    if not install_requirements():
        print("Failed to install requirements. Please check your Python environment.")
        return False
    
    # Download spaCy models
    print("\n3. Downloading spaCy models...")
    if not download_spacy_models():
        print("Warning: Some spaCy models failed to download.")
        print("You can download them manually later using:")
        print("python -m spacy download en_core_web_sm")
    
    print("\n" + "=" * 60)
    print("Setup completed!")
    print("=" * 60)
    print("\nYou can now run:")
    print("• streamlit run web_app.py          # Web interface")
    print("• python ner_api.py                # REST API")
    print("• python batch_processor.py --help # Batch processing")
    print("• python custom_entity_trainer.py  # Custom training")
    print("• python multilingual_ner.py       # Multilingual demo")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
