#!/usr/bin/env python3
"""
Test script to verify NER functionality
"""

import spacy
from textblob import TextBlob

def test_basic_ner():
    """Test basic NER functionality"""
    print("Testing Basic NER Functionality")
    print("=" * 50)
    
    try:
        # Load spaCy model
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy model loaded successfully")
        
        # Test text
        text = "Apple Inc. is looking at buying U.K. startup for $1 billion"
        doc = nlp(text)
        
        print(f"\nAnalyzing: '{text}'")
        print("\nEntities found:")
        
        if doc.ents:
            for ent in doc.ents:
                print(f"  - {ent.text} ({ent.label_}) - {spacy.explain(ent.label_)}")
        else:
            print("  No entities found")
        
        # Test sentiment analysis
        blob = TextBlob(text)
        print(f"\nSentiment Analysis:")
        print(f"  Polarity: {blob.sentiment.polarity:.2f}")
        print(f"  Subjectivity: {blob.sentiment.subjectivity:.2f}")
        
        print("\n✓ Basic NER test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_advanced_features():
    """Test advanced NER features"""
    print("\nTesting Advanced Features")
    print("=" * 50)
    
    try:
        nlp = spacy.load('en_core_web_sm')
        
        # More complex text
        text = """
        When Sebastian Thrun started working on self-driving cars at Google in 2007,
        few people outside of the company took him seriously. "I can tell you very senior
        CEOs of major American car companies would shake my hand and turn away because
        I wasn't worth talking to," said Thrun, in an interview with Recode earlier this week.
        """
        
        doc = nlp(text)
        
        print(f"Text statistics:")
        print(f"  Words: {len([token for token in doc if not token.is_space])}")
        print(f"  Sentences: {len(list(doc.sents))}")
        print(f"  Entities: {len(doc.ents)}")
        
        print(f"\nEntities found:")
        for ent in doc.ents:
            print(f"  - {ent.text} ({ent.label_}) - {spacy.explain(ent.label_)}")
        
        print("\n✓ Advanced features test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("NER Project Test Suite")
    print("=" * 60)
    
    # Run tests
    basic_test = test_basic_ner()
    advanced_test = test_advanced_features()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"Basic NER: {'PASS' if basic_test else 'FAIL'}")
    print(f"Advanced Features: {'PASS' if advanced_test else 'FAIL'}")
    
    if basic_test and advanced_test:
        print("\n🎉 All tests passed! The NER project is ready to run.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
