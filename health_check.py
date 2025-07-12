#!/usr/bin/env python3
"""
Health check script for Render deployment
"""

import sys
import subprocess

def check_dependencies():
    """Check if all dependencies are working"""
    print("🔍 Checking dependencies...")
    
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import spacy
        print(f"✅ spaCy: {spacy.__version__}")
        
        # Try to load model
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy model: en_core_web_sm loaded")
        except OSError:
            print("⚠️  spaCy model: en_core_web_sm not found")
            return False
            
    except ImportError as e:
        print(f"❌ spaCy: {e}")
        return False
    
    try:
        import textblob
        print(f"✅ TextBlob: {textblob.__version__}")
    except ImportError as e:
        print(f"⚠️  TextBlob: {e} (optional)")
    
    return True

def test_basic_functionality():
    """Test basic NER functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        
        test_text = "Apple Inc. is based in California"
        doc = nlp(test_text)
        
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"✅ NER test: Found {len(entities)} entities")
        
        for text, label in entities:
            print(f"   - {text} ({label})")
        
        return True
        
    except Exception as e:
        print(f"❌ NER test failed: {e}")
        return False

def main():
    print("🏥 Health Check for Advanced NER Suite")
    print("=" * 50)
    
    deps_ok = check_dependencies()
    func_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if deps_ok and func_ok:
        print("🎉 Health check PASSED - Ready for deployment!")
        sys.exit(0)
    else:
        print("❌ Health check FAILED - Issues detected")
        sys.exit(1)

if __name__ == "__main__":
    main()
