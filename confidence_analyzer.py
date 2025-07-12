import spacy
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Tuple
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import warnings
warnings.filterwarnings('ignore')

@dataclass
class EntityConfidence:
    text: str
    label: str
    start: int
    end: int
    confidence: float
    uncertainty: float
    context_strength: float
    model_agreement: float

class AdvancedConfidenceAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        
        # Load transformer model for comparison
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            self.transformer_model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            self.has_transformer = True
        except:
            self.has_transformer = False
            st.warning("Transformer model not available. Using spaCy only.")
    
    def calculate_context_strength(self, doc, entity) -> float:
        """Calculate how strong the context is for entity prediction"""
        # Get surrounding context (5 words before and after)
        start_idx = max(0, entity.start - 5)
        end_idx = min(len(doc), entity.end + 5)
        
        context_tokens = doc[start_idx:end_idx]
        
        # Calculate context strength based on:
        # 1. POS tags consistency
        # 2. Dependency relationships
        # 3. Capitalization patterns
        
        strength_score = 0.5  # Base score
        
        # Check capitalization pattern
        if entity.text[0].isupper():
            strength_score += 0.2
        
        # Check if entity is subject/object of sentence
        if entity.root.dep_ in ['nsubj', 'dobj', 'pobj']:
            strength_score += 0.2
        
        # Check surrounding POS tags
        surrounding_pos = [token.pos_ for token in context_tokens if token != entity]
        if any(pos in ['DET', 'ADJ'] for pos in surrounding_pos):
            strength_score += 0.1
        
        return min(1.0, strength_score)
    
    def get_transformer_predictions(self, text: str) -> List[Dict]:
        """Get predictions from transformer model"""
        if not self.has_transformer:
            return []
        
        try:
            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Convert to entities
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            predicted_labels = torch.argmax(predictions, dim=-1)[0]
            confidences = torch.max(predictions, dim=-1)[0][0]
            
            entities = []
            current_entity = None
            
            for i, (token, label_id, conf) in enumerate(zip(tokens, predicted_labels, confidences)):
                label = self.transformer_model.config.id2label[label_id.item()]
                
                if label.startswith('B-'):  # Beginning of entity
                    if current_entity:
                        entities.append(current_entity)
                    current_entity = {
                        'text': token.replace('##', ''),
                        'label': label[2:],
                        'confidence': conf.item(),
                        'start': i,
                        'end': i + 1
                    }
                elif label.startswith('I-') and current_entity:  # Inside entity
                    current_entity['text'] += token.replace('##', '')
                    current_entity['end'] = i + 1
                    current_entity['confidence'] = (current_entity['confidence'] + conf.item()) / 2
                else:  # Outside entity
                    if current_entity:
                        entities.append(current_entity)
                        current_entity = None
            
            if current_entity:
                entities.append(current_entity)
            
            return entities
        
        except Exception as e:
            print(f"Error in transformer prediction: {e}")
            return []
    
    def calculate_model_agreement(self, spacy_entities: List, transformer_entities: List) -> Dict[str, float]:
        """Calculate agreement between spaCy and transformer models"""
        if not transformer_entities:
            return {ent.text: 0.5 for ent in spacy_entities}  # Default neutral agreement
        
        agreement_scores = {}
        
        for spacy_ent in spacy_entities:
            max_agreement = 0.0
            
            for trans_ent in transformer_entities:
                # Check text overlap
                text_overlap = len(set(spacy_ent.text.lower().split()) & 
                                set(trans_ent['text'].lower().split()))
                total_words = len(set(spacy_ent.text.lower().split()) | 
                                set(trans_ent['text'].lower().split()))
                
                if total_words > 0:
                    text_similarity = text_overlap / total_words
                    
                    # Check label agreement
                    label_agreement = 1.0 if spacy_ent.label_ == trans_ent['label'] else 0.0
                    
                    # Combined agreement
                    agreement = (text_similarity * 0.7 + label_agreement * 0.3)
                    max_agreement = max(max_agreement, agreement)
            
            agreement_scores[spacy_ent.text] = max_agreement
        
        return agreement_scores
    
    def analyze_entity_confidence(self, text: str) -> List[EntityConfidence]:
        """Comprehensive entity confidence analysis"""
        doc = self.nlp(text)
        
        # Get transformer predictions for comparison
        transformer_entities = self.get_transformer_predictions(text)
        
        # Calculate model agreement
        model_agreements = self.calculate_model_agreement(doc.ents, transformer_entities)
        
        confident_entities = []
        
        for ent in doc.ents:
            # Base confidence from spaCy (if available)
            base_confidence = getattr(ent, 'confidence', 0.8)
            
            # Context strength
            context_strength = self.calculate_context_strength(doc, ent)
            
            # Model agreement
            model_agreement = model_agreements.get(ent.text, 0.5)
            
            # Calculate uncertainty (inverse of confidence with context)
            uncertainty = 1.0 - (base_confidence * context_strength * model_agreement)
            
            # Final confidence score
            final_confidence = (base_confidence * 0.4 + 
                              context_strength * 0.3 + 
                              model_agreement * 0.3)
            
            confident_entities.append(EntityConfidence(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=final_confidence,
                uncertainty=uncertainty,
                context_strength=context_strength,
                model_agreement=model_agreement
            ))
        
        return confident_entities
    
    def create_confidence_visualization(self, entities: List[EntityConfidence]) -> go.Figure:
        """Create confidence visualization"""
        if not entities:
            return None
        
        # Prepare data
        entity_names = [ent.text for ent in entities]
        confidences = [ent.confidence for ent in entities]
        uncertainties = [ent.uncertainty for ent in entities]
        context_strengths = [ent.context_strength for ent in entities]
        model_agreements = [ent.model_agreement for ent in entities]
        labels = [ent.label for ent in entities]
        
        # Create subplot
        fig = go.Figure()
        
        # Add confidence bars
        fig.add_trace(go.Bar(
            name='Confidence',
            x=entity_names,
            y=confidences,
            marker_color='lightblue',
            text=[f'{c:.2f}' for c in confidences],
            textposition='auto',
        ))
        
        # Add uncertainty line
        fig.add_trace(go.Scatter(
            name='Uncertainty',
            x=entity_names,
            y=uncertainties,
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Entity Confidence Analysis',
            xaxis_title='Entities',
            yaxis_title='Confidence Score',
            yaxis2=dict(
                title='Uncertainty',
                overlaying='y',
                side='right',
                range=[0, 1]
            ),
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def create_confidence_heatmap(self, entities: List[EntityConfidence]) -> go.Figure:
        """Create confidence metrics heatmap"""
        if not entities:
            return None
        
        metrics = ['Confidence', 'Context Strength', 'Model Agreement', 'Uncertainty']
        entity_names = [ent.text[:15] + '...' if len(ent.text) > 15 else ent.text for ent in entities]
        
        data = [
            [ent.confidence for ent in entities],
            [ent.context_strength for ent in entities],
            [ent.model_agreement for ent in entities],
            [1 - ent.uncertainty for ent in entities]  # Invert uncertainty for better visualization
        ]
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=entity_names,
            y=metrics,
            colorscale='RdYlBu',
            text=[[f'{val:.2f}' for val in row] for row in data],
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Entity Confidence Metrics Heatmap',
            height=400
        )
        
        return fig

def create_confidence_interface():
    """Streamlit interface for confidence analysis"""
    st.title("🎯 Entity Confidence & Uncertainty Analysis")
    st.markdown("Advanced analysis of entity prediction confidence with multi-model comparison")
    
    # Initialize analyzer
    if 'conf_analyzer' not in st.session_state:
        with st.spinner("Loading confidence analyzer..."):
            st.session_state.conf_analyzer = AdvancedConfidenceAnalyzer()
    
    analyzer = st.session_state.conf_analyzer
    
    # Input
    text_input = st.text_area(
        "Enter text for confidence analysis:",
        placeholder="Enter text with named entities...",
        height=150
    )
    
    if st.button("🔍 Analyze Confidence") and text_input:
        with st.spinner("Analyzing entity confidence..."):
            entities = analyzer.analyze_entity_confidence(text_input)
        
        if entities:
            # Display results
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Confidence Scores")
                for ent in entities:
                    confidence_color = "🟢" if ent.confidence > 0.8 else "🟡" if ent.confidence > 0.6 else "🔴"
                    st.write(f"{confidence_color} **{ent.text}** ({ent.label})")
                    st.write(f"   Confidence: {ent.confidence:.2f}")
                    st.write(f"   Context Strength: {ent.context_strength:.2f}")
                    st.write(f"   Model Agreement: {ent.model_agreement:.2f}")
                    st.write(f"   Uncertainty: {ent.uncertainty:.2f}")
                    st.write("---")
            
            with col2:
                st.subheader("📈 Confidence Statistics")
                avg_confidence = np.mean([ent.confidence for ent in entities])
                avg_uncertainty = np.mean([ent.uncertainty for ent in entities])
                high_conf_count = sum(1 for ent in entities if ent.confidence > 0.8)
                
                st.metric("Average Confidence", f"{avg_confidence:.2f}")
                st.metric("Average Uncertainty", f"{avg_uncertainty:.2f}")
                st.metric("High Confidence Entities", f"{high_conf_count}/{len(entities)}")
            
            # Visualizations
            st.subheader("📊 Confidence Visualizations")
            
            # Confidence chart
            conf_fig = analyzer.create_confidence_visualization(entities)
            if conf_fig:
                st.plotly_chart(conf_fig, use_container_width=True)
            
            # Heatmap
            heatmap_fig = analyzer.create_confidence_heatmap(entities)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig, use_container_width=True)
        
        else:
            st.info("No entities found in the text")

if __name__ == "__main__":
    create_confidence_interface()
