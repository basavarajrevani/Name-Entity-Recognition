#!/usr/bin/env python3
"""
Complete demonstration script for Advanced NER Suite
This script tests all major features and provides a comprehensive demo
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def test_basic_imports():
    """Test if all required packages are installed"""
    print_step("1", "Testing Package Imports")
    
    try:
        import spacy
        print("✅ spaCy imported successfully")
        
        import streamlit
        print("✅ Streamlit imported successfully")
        
        import fastapi
        print("✅ FastAPI imported successfully")
        
        import plotly
        print("✅ Plotly imported successfully")
        
        import transformers
        print("✅ Transformers imported successfully")
        
        import networkx
        print("✅ NetworkX imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_spacy_models():
    """Test if spaCy models are available"""
    print_step("2", "Testing spaCy Models")
    
    try:
        import spacy
        
        # Test English model
        nlp = spacy.load('en_core_web_sm')
        print("✅ English model (en_core_web_sm) loaded")
        
        # Test basic NER
        doc = nlp("Apple Inc. is based in California")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"✅ Basic NER test: Found {len(entities)} entities")
        for text, label in entities:
            print(f"   - {text} ({label})")
        
        return True
    except Exception as e:
        print(f"❌ spaCy model error: {e}")
        return False

def test_core_functionality():
    """Test core NER functionality"""
    print_step("3", "Testing Core NER Functionality")
    
    try:
        # Import our modules
        sys.path.append('.')
        
        # Test basic analysis
        import spacy
        from textblob import TextBlob
        
        nlp = spacy.load('en_core_web_sm')
        
        test_text = """
        Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
        Tim Cook became CEO in 2011, succeeding Steve Jobs. The company reported revenue of $394.3 billion in 2022.
        Major competitors include Samsung, Google, Microsoft, and Amazon.
        """
        
        doc = nlp(test_text)
        blob = TextBlob(test_text)
        
        print(f"✅ Processed text with {len(doc)} tokens")
        print(f"✅ Found {len(doc.ents)} entities")
        print(f"✅ Sentiment: {blob.sentiment.polarity:.2f}")
        
        # Show entities
        print("\n📋 Entities found:")
        for ent in doc.ents:
            print(f"   - {ent.text} ({ent.label_}) - {spacy.explain(ent.label_)}")
        
        return True
    except Exception as e:
        print(f"❌ Core functionality error: {e}")
        return False

def start_demo_app():
    """Start the demo application"""
    print_step("4", "Starting Demo Application")
    
    try:
        # Start the demo app in background
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "demo_all_features.py",
            "--server.port", "8502",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for startup
        time.sleep(10)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Demo application started successfully")
            print("🌐 Access at: http://localhost:8502")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Demo app failed to start")
            print(f"Error: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting demo app: {e}")
        return None

def start_api_server():
    """Start the API server"""
    print_step("5", "Starting API Server")
    
    try:
        # Start API server in background
        process = subprocess.Popen([
            sys.executable, "ner_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        time.sleep(8)
        
        # Test API health
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully")
                print("🌐 API at: http://localhost:8000")
                print("📚 Docs at: http://localhost:8000/docs")
                return process
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ API server not responding")
            return None
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def test_api_endpoints():
    """Test API endpoints"""
    print_step("6", "Testing API Endpoints")
    
    try:
        # Test analyze endpoint
        response = requests.post("http://localhost:8000/analyze", 
            json={
                "text": "Microsoft was founded by Bill Gates in Redmond, Washington",
                "include_sentiment": True
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /analyze endpoint working")
            print(f"   Found {len(result['entities'])} entities")
            print(f"   Sentiment: {result.get('sentiment', {}).get('polarity', 'N/A')}")
        else:
            print(f"❌ /analyze endpoint failed: {response.status_code}")
        
        # Test batch endpoint
        response = requests.post("http://localhost:8000/batch",
            json={
                "texts": [
                    "Google is based in Mountain View",
                    "Tesla was founded by Elon Musk"
                ]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /batch endpoint working")
            print(f"   Processed {len(result['results'])} texts")
        else:
            print(f"❌ /batch endpoint failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ API testing error: {e}")
        return False

def test_batch_processing():
    """Test batch processing functionality"""
    print_step("7", "Testing Batch Processing")
    
    try:
        # Create test document
        test_doc = Path("test_batch_doc.txt")
        test_doc.write_text("""
        Amazon was founded by Jeff Bezos in Seattle, Washington in 1994.
        The company started as an online bookstore but expanded to become
        one of the world's largest e-commerce and cloud computing companies.
        Andy Jassy became CEO in 2021, succeeding Jeff Bezos.
        """)
        
        # Run batch processor
        result = subprocess.run([
            sys.executable, "batch_processor.py", 
            str(test_doc), 
            "--output", "test_batch_results",
            "--format", "json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Batch processing completed successfully")
            
            # Check if output file exists
            output_file = Path("test_batch_results.json")
            if output_file.exists():
                print("✅ Output file created")
                
                # Load and show results
                with open(output_file) as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        entities = data[0].get('entities', [])
                        print(f"   Found {len(entities)} entities in batch processing")
                
                # Cleanup
                output_file.unlink()
            
            # Cleanup test file
            test_doc.unlink()
        else:
            print(f"❌ Batch processing failed: {result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def show_summary(results):
    """Show test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your NER Suite is ready to use!")
        print("\n🚀 Next Steps:")
        print("   1. Open http://localhost:8502 for the demo")
        print("   2. Open http://localhost:8000/docs for API docs")
        print("   3. Try different features and text samples")
        print("   4. Explore the advanced AI features")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Refer to SETUP_GUIDE.md for troubleshooting")

def main():
    """Main demo function"""
    print_header("Advanced NER Suite - Complete Demo")
    print("This script will test all major features of the NER Suite")
    print("Please wait while we run comprehensive tests...")
    
    # Store test results
    results = {}
    
    # Run tests
    results["Package Imports"] = test_basic_imports()
    results["spaCy Models"] = test_spacy_models()
    results["Core Functionality"] = test_core_functionality()
    
    # Start services
    demo_process = start_demo_app()
    api_process = start_api_server()
    
    results["Demo Application"] = demo_process is not None
    results["API Server"] = api_process is not None
    
    if api_process:
        results["API Endpoints"] = test_api_endpoints()
    else:
        results["API Endpoints"] = False
    
    results["Batch Processing"] = test_batch_processing()
    
    # Show summary
    show_summary(results)
    
    # Keep services running
    if demo_process or api_process:
        print("\n🔄 Services are running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            if demo_process:
                demo_process.terminate()
            if api_process:
                api_process.terminate()
            print("✅ Services stopped. Goodbye!")

if __name__ == "__main__":
    main()
