import streamlit as st
import spacy
from spacy import displacy
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# Load spaCy model
@st.cache_resource
def load_nlp_model():
    return spacy.load('en_core_web_sm')

nlp = load_nlp_model()

def analyze_text_advanced(text):
    doc = nlp(text)
    
    # Extract entities
    entities = [(ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
    
    # Sentiment analysis
    sentiment = TextBlob(text).sentiment
    
    # Extract key statistics
    stats = {
        'word_count': len([token for token in doc if not token.is_space]),
        'sentence_count': len(list(doc.sents)),
        'entity_count': len(entities),
        'unique_entities': len(set([ent[0] for ent in entities]))
    }
    
    return doc, entities, sentiment, stats

def create_entity_chart(entities):
    if not entities:
        return None
    
    entity_counts = Counter([ent[1] for ent in entities])
    df = pd.DataFrame(list(entity_counts.items()), columns=['Entity Type', 'Count'])
    
    fig = px.bar(df, x='Entity Type', y='Count', 
                 title='Named Entity Distribution',
                 color='Count',
                 color_continuous_scale='viridis')
    return fig

def main():
    st.set_page_config(page_title="Advanced NER Analyzer", layout="wide")

    st.title("🔍 Advanced Named Entity Recognition Analyzer")
    st.markdown("Comprehensive NLP analysis with cutting-edge AI features")

    # Sidebar navigation
    st.sidebar.title("🚀 NER Features")

    # Feature selection
    feature = st.sidebar.selectbox(
        "Choose Analysis Type:",
        [
            "🔍 Basic NER Analysis",
            "🧠 Knowledge Graph NER",
            "🎯 Confidence Analysis",
            "🔄 Collaborative Annotation",
            "🎨 Advanced Visualization",
            "🌍 Multilingual Analysis"
        ]
    )

    # Route to different features
    if feature == "🔍 Basic NER Analysis":
        basic_ner_interface()
    elif feature == "🧠 Knowledge Graph NER":
        from knowledge_graph_ner import create_knowledge_graph_interface
        create_knowledge_graph_interface()
    elif feature == "🎯 Confidence Analysis":
        from confidence_analyzer import create_confidence_interface
        create_confidence_interface()
    elif feature == "🔄 Collaborative Annotation":
        from collaborative_annotation import create_annotation_interface
        create_annotation_interface()
    elif feature == "🎨 Advanced Visualization":
        from advanced_visualization import create_advanced_visualization_interface
        create_advanced_visualization_interface()
    elif feature == "🌍 Multilingual Analysis":
        from multilingual_ner import create_multilingual_interface
        create_multilingual_interface()

def basic_ner_interface():
    """Basic NER analysis interface"""
    st.header("🔍 Basic Named Entity Recognition")

    # Sidebar for options
    st.sidebar.header("Analysis Options")
    show_entities = st.sidebar.checkbox("Show Named Entities", True)
    show_sentiment = st.sidebar.checkbox("Show Sentiment Analysis", True)
    show_stats = st.sidebar.checkbox("Show Text Statistics", True)
    show_visualization = st.sidebar.checkbox("Show Entity Visualization", True)

    # Main input
    text_input = st.text_area("Enter text to analyze:",
                             placeholder="Paste your text here...",
                             height=200)
    
    if st.button("Analyze Text") and text_input:
        doc, entities, sentiment, stats = analyze_text_advanced(text_input)
        
        # Create columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if show_entities and entities:
                st.subheader("📋 Named Entities")
                entity_df = pd.DataFrame(entities, 
                                       columns=['Entity', 'Type', 'Start', 'End'])
                st.dataframe(entity_df, use_container_width=True)
                
                # Entity visualization
                st.subheader("🎨 Entity Visualization")
                html = displacy.render(doc, style="ent", jupyter=False)
                st.components.v1.html(html, height=300, scrolling=True)
        
        with col2:
            if show_stats:
                st.subheader("📊 Text Statistics")
                st.metric("Words", stats['word_count'])
                st.metric("Sentences", stats['sentence_count'])
                st.metric("Entities Found", stats['entity_count'])
                st.metric("Unique Entities", stats['unique_entities'])
            
            if show_sentiment:
                st.subheader("😊 Sentiment Analysis")
                st.metric("Polarity", f"{sentiment.polarity:.2f}")
                st.metric("Subjectivity", f"{sentiment.subjectivity:.2f}")
                
                # Sentiment gauge
                sentiment_label = "Positive" if sentiment.polarity > 0 else "Negative" if sentiment.polarity < 0 else "Neutral"
                st.write(f"**Overall Sentiment:** {sentiment_label}")
        
        if show_visualization and entities:
            st.subheader("📈 Entity Distribution Chart")
            chart = create_entity_chart(entities)
            if chart:
                st.plotly_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
