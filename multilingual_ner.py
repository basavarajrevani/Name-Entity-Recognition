import spacy
from langdetect import detect
import streamlit as st
from collections import defaultdict

class MultilingualNER:
    def __init__(self):
        """Initialize multilingual NER with support for multiple languages"""
        self.models = {}
        self.supported_languages = {
            'en': 'en_core_web_sm',
            'es': 'es_core_news_sm',
            'fr': 'fr_core_news_sm',
            'de': 'de_core_news_sm',
            'it': 'it_core_news_sm',
            'pt': 'pt_core_news_sm',
            'nl': 'nl_core_news_sm',
            'zh': 'zh_core_web_sm'
        }
        
        # Load available models
        self.load_available_models()
    
    def load_available_models(self):
        """Load all available spaCy models"""
        for lang_code, model_name in self.supported_languages.items():
            try:
                self.models[lang_code] = spacy.load(model_name)
                print(f"✓ Loaded {model_name} for {lang_code}")
            except OSError:
                print(f"✗ Model {model_name} not found for {lang_code}")
                print(f"  Install with: python -m spacy download {model_name}")
    
    def detect_language(self, text):
        """Detect the language of the input text"""
        try:
            detected_lang = detect(text)
            return detected_lang if detected_lang in self.models else 'en'
        except:
            return 'en'  # Default to English
    
    def analyze_text(self, text, language=None):
        """Analyze text in the specified or detected language"""
        if language is None:
            language = self.detect_language(text)
        
        if language not in self.models:
            print(f"Language {language} not supported, using English")
            language = 'en'
        
        if language not in self.models:
            raise ValueError("No models available. Please install at least en_core_web_sm")
        
        nlp = self.models[language]
        doc = nlp(text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'description': spacy.explain(ent.label_)
            })
        
        # Extract linguistic features
        tokens = []
        for token in doc:
            if not token.is_space:
                tokens.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'pos': token.pos_,
                    'tag': token.tag_,
                    'dep': token.dep_
                })
        
        return {
            'language': language,
            'entities': entities,
            'tokens': tokens,
            'sentences': [sent.text for sent in doc.sents]
        }
    
    def compare_languages(self, texts_dict):
        """Compare NER results across multiple languages"""
        results = {}
        
        for lang, text in texts_dict.items():
            if lang in self.models:
                results[lang] = self.analyze_text(text, lang)
        
        return results
    
    def get_entity_statistics(self, results):
        """Get statistics about entities across languages"""
        stats = defaultdict(lambda: defaultdict(int))
        
        for lang, result in results.items():
            for entity in result['entities']:
                stats[lang][entity['label']] += 1
        
        return dict(stats)

# Streamlit interface for multilingual NER
def create_multilingual_interface():
    st.title("🌍 Multilingual Named Entity Recognition")
    
    # Initialize multilingual NER
    if 'multilingual_ner' not in st.session_state:
        st.session_state.multilingual_ner = MultilingualNER()
    
    ner = st.session_state.multilingual_ner
    
    # Show available languages
    available_langs = list(ner.models.keys())
    st.sidebar.header("Available Languages")
    for lang in available_langs:
        st.sidebar.write(f"✓ {lang.upper()}")
    
    # Language selection
    language_options = ['Auto-detect'] + available_langs
    selected_language = st.selectbox("Select Language:", language_options)
    
    # Text input
    text_input = st.text_area("Enter text to analyze:", height=150)
    
    if st.button("Analyze") and text_input:
        # Determine language
        if selected_language == 'Auto-detect':
            detected_lang = ner.detect_language(text_input)
            st.info(f"Detected language: {detected_lang.upper()}")
            analysis_lang = detected_lang
        else:
            analysis_lang = selected_language
        
        # Perform analysis
        try:
            result = ner.analyze_text(text_input, analysis_lang)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Named Entities")
                if result['entities']:
                    for entity in result['entities']:
                        st.write(f"**{entity['text']}** - {entity['label']} ({entity['description']})")
                else:
                    st.write("No entities found")
            
            with col2:
                st.subheader("Language Info")
                st.write(f"**Language:** {result['language'].upper()}")
                st.write(f"**Sentences:** {len(result['sentences'])}")
                st.write(f"**Tokens:** {len(result['tokens'])}")
                st.write(f"**Entities:** {len(result['entities'])}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Example texts in different languages
SAMPLE_TEXTS = {
    'en': "Apple Inc. is an American multinational technology company headquartered in Cupertino, California.",
    'es': "Apple Inc. es una empresa multinacional estadounidense de tecnología con sede en Cupertino, California.",
    'fr': "Apple Inc. est une entreprise multinationale américaine de technologie basée à Cupertino, en Californie.",
    'de': "Apple Inc. ist ein amerikanisches multinationales Technologieunternehmen mit Hauptsitz in Cupertino, Kalifornien.",
    'it': "Apple Inc. è un'azienda multinazionale americana di tecnologia con sede a Cupertino, in California.",
    'pt': "A Apple Inc. é uma empresa multinacional americana de tecnologia sediada em Cupertino, Califórnia."
}

def demo_multilingual_analysis():
    """Demonstrate multilingual analysis capabilities"""
    ner = MultilingualNER()
    
    print("Multilingual NER Analysis Demo")
    print("=" * 50)
    
    # Analyze sample texts
    for lang, text in SAMPLE_TEXTS.items():
        if lang in ner.models:
            print(f"\nAnalyzing {lang.upper()}: {text}")
            result = ner.analyze_text(text, lang)
            
            print("Entities found:")
            for entity in result['entities']:
                print(f"  - {entity['text']} ({entity['label']})")

if __name__ == "__main__":
    # Run demo
    demo_multilingual_analysis()
