import spacy
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import networkx as nx
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
import json

class AdvancedEntityVisualizer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.color_palette = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4',
            'GPE': '#45B7D1',
            'MONEY': '#96CEB4',
            'DATE': '#FFEAA7',
            'TIME': '#DDA0DD',
            'PERCENT': '#98D8C8',
            'CARDINAL': '#F7DC6F',
            'ORDINAL': '#BB8FCE',
            'QUANTITY': '#85C1E9'
        }
    
    def analyze_text_comprehensive(self, text: str) -> Dict:
        """Comprehensive text analysis"""
        doc = self.nlp(text)
        
        # Extract entities with detailed info
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'sentence_id': None,  # Will be filled below
                'pos_context': [token.pos_ for token in ent],
                'dependency': ent.root.dep_,
                'head': ent.root.head.text
            })
        
        # Add sentence context
        sentences = list(doc.sents)
        for i, sent in enumerate(sentences):
            for entity in entities:
                if entity['start'] >= sent.start_char and entity['end'] <= sent.end_char:
                    entity['sentence_id'] = i
        
        # Entity co-occurrence matrix
        cooccurrence = defaultdict(lambda: defaultdict(int))
        for sent in sentences:
            sent_entities = [ent.text for ent in sent.ents]
            for i, ent1 in enumerate(sent_entities):
                for ent2 in sent_entities[i+1:]:
                    cooccurrence[ent1][ent2] += 1
                    cooccurrence[ent2][ent1] += 1
        
        # Temporal analysis (for DATE entities)
        temporal_entities = [ent for ent in entities if ent['label'] == 'DATE']
        
        # Sentiment by entity (basic)
        entity_sentiments = {}
        for ent in doc.ents:
            # Get sentence containing entity
            for sent in sentences:
                if ent.start_char >= sent.start_char and ent.end_char <= sent.end_char:
                    # Simple sentiment based on surrounding words
                    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'success']
                    negative_words = ['bad', 'terrible', 'awful', 'failure', 'problem', 'issue']
                    
                    sent_text = sent.text.lower()
                    pos_count = sum(1 for word in positive_words if word in sent_text)
                    neg_count = sum(1 for word in negative_words if word in sent_text)
                    
                    if pos_count > neg_count:
                        sentiment = 'positive'
                    elif neg_count > pos_count:
                        sentiment = 'negative'
                    else:
                        sentiment = 'neutral'
                    
                    entity_sentiments[ent.text] = sentiment
                    break
        
        return {
            'entities': entities,
            'sentences': [sent.text for sent in sentences],
            'cooccurrence': dict(cooccurrence),
            'temporal_entities': temporal_entities,
            'entity_sentiments': entity_sentiments,
            'stats': {
                'total_entities': len(entities),
                'unique_entities': len(set(ent['text'] for ent in entities)),
                'entity_types': len(set(ent['label'] for ent in entities)),
                'sentences': len(sentences)
            }
        }
    
    def create_entity_timeline(self, entities: List[Dict]) -> go.Figure:
        """Create timeline visualization for temporal entities"""
        date_entities = [ent for ent in entities if ent['label'] == 'DATE']
        
        if not date_entities:
            return None
        
        # Simple timeline based on order of appearance
        fig = go.Figure()
        
        for i, ent in enumerate(date_entities):
            fig.add_trace(go.Scatter(
                x=[i],
                y=[ent['text']],
                mode='markers+text',
                text=ent['text'],
                textposition='middle right',
                marker=dict(size=15, color=self.color_palette.get('DATE', '#FFEAA7')),
                name=f"Date {i+1}"
            ))
        
        fig.update_layout(
            title="Temporal Entity Timeline",
            xaxis_title="Order of Appearance",
            yaxis_title="Date Entities",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_entity_network(self, cooccurrence: Dict) -> go.Figure:
        """Create entity co-occurrence network"""
        if not cooccurrence:
            return None
        
        # Create network graph
        G = nx.Graph()
        
        # Add edges with weights
        for entity1, connections in cooccurrence.items():
            for entity2, weight in connections.items():
                if weight > 0:  # Only add if there's co-occurrence
                    G.add_edge(entity1, entity2, weight=weight)
        
        if not G.nodes():
            return None
        
        # Calculate layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Prepare traces
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(G[edge[0]][edge[1]]['weight'])
        
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            # Node size based on degree
            node_size.append(max(20, G.degree(node) * 10))
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Co-occurrence'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_size,
                color='lightblue',
                line=dict(width=2, color='white')
            ),
            name='Entities'
        ))
        
        fig.update_layout(
            title="Entity Co-occurrence Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500
        )
        
        return fig
    
    def create_entity_heatmap(self, entities: List[Dict]) -> go.Figure:
        """Create entity type distribution heatmap"""
        # Count entities by type and sentence
        sentence_entity_counts = defaultdict(lambda: defaultdict(int))
        
        for ent in entities:
            if ent['sentence_id'] is not None:
                sentence_entity_counts[ent['sentence_id']][ent['label']] += 1
        
        if not sentence_entity_counts:
            return None
        
        # Prepare data for heatmap
        sentences = sorted(sentence_entity_counts.keys())
        entity_types = sorted(set(ent['label'] for ent in entities))
        
        heatmap_data = []
        for sentence_id in sentences:
            row = []
            for entity_type in entity_types:
                row.append(sentence_entity_counts[sentence_id][entity_type])
            heatmap_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=entity_types,
            y=[f"Sentence {i+1}" for i in sentences],
            colorscale='Blues',
            text=heatmap_data,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Entity Distribution Across Sentences",
            xaxis_title="Entity Types",
            yaxis_title="Sentences",
            height=400
        )
        
        return fig
    
    def create_entity_wordcloud(self, entities: List[Dict]) -> plt.Figure:
        """Create word cloud of entities"""
        if not entities:
            return None
        
        # Create frequency dictionary
        entity_freq = Counter(ent['text'] for ent in entities)
        
        if not entity_freq:
            return None
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate_from_frequencies(entity_freq)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Entity Word Cloud', fontsize=16, fontweight='bold')
        
        return fig
    
    def create_sentiment_analysis(self, entity_sentiments: Dict) -> go.Figure:
        """Create sentiment analysis visualization"""
        if not entity_sentiments:
            return None
        
        sentiment_counts = Counter(entity_sentiments.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(sentiment_counts.keys()),
                y=list(sentiment_counts.values()),
                marker_color=['green' if s == 'positive' else 'red' if s == 'negative' else 'gray' 
                             for s in sentiment_counts.keys()]
            )
        ])
        
        fig.update_layout(
            title="Entity Sentiment Distribution",
            xaxis_title="Sentiment",
            yaxis_title="Count",
            height=400
        )
        
        return fig
    
    def create_entity_stats_dashboard(self, analysis: Dict) -> go.Figure:
        """Create comprehensive stats dashboard"""
        stats = analysis['stats']
        
        # Create subplots
        fig = go.Figure()
        
        # Entity type distribution
        entity_types = Counter(ent['label'] for ent in analysis['entities'])
        
        fig.add_trace(go.Bar(
            x=list(entity_types.keys()),
            y=list(entity_types.values()),
            name='Entity Types',
            marker_color=[self.color_palette.get(et, '#95A5A6') for et in entity_types.keys()]
        ))
        
        fig.update_layout(
            title="Entity Type Distribution",
            xaxis_title="Entity Types",
            yaxis_title="Count",
            height=400
        )
        
        return fig

def create_advanced_visualization_interface():
    """Streamlit interface for advanced visualization"""
    st.title("🎨 Advanced Entity Visualization & Analytics")
    st.markdown("Comprehensive entity analysis with interactive visualizations")
    
    # Initialize visualizer
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = AdvancedEntityVisualizer()
    
    visualizer = st.session_state.visualizer
    
    # Input
    text_input = st.text_area(
        "Enter text for advanced analysis:",
        placeholder="Enter text with multiple entities for comprehensive analysis...",
        height=200
    )
    
    if st.button("🔍 Analyze & Visualize") and text_input:
        with st.spinner("Performing comprehensive analysis..."):
            analysis = visualizer.analyze_text_comprehensive(text_input)
        
        # Display basic stats
        st.subheader("📊 Analysis Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entities", analysis['stats']['total_entities'])
        with col2:
            st.metric("Unique Entities", analysis['stats']['unique_entities'])
        with col3:
            st.metric("Entity Types", analysis['stats']['entity_types'])
        with col4:
            st.metric("Sentences", analysis['stats']['sentences'])
        
        # Visualizations
        st.subheader("📈 Interactive Visualizations")
        
        # Entity type distribution
        stats_fig = visualizer.create_entity_stats_dashboard(analysis)
        if stats_fig:
            st.plotly_chart(stats_fig, use_container_width=True)
        
        # Entity network
        network_fig = visualizer.create_entity_network(analysis['cooccurrence'])
        if network_fig:
            st.plotly_chart(network_fig, use_container_width=True)
        
        # Entity heatmap
        heatmap_fig = visualizer.create_entity_heatmap(analysis['entities'])
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # Timeline for temporal entities
        timeline_fig = visualizer.create_entity_timeline(analysis['entities'])
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Sentiment analysis
        sentiment_fig = visualizer.create_sentiment_analysis(analysis['entity_sentiments'])
        if sentiment_fig:
            st.plotly_chart(sentiment_fig, use_container_width=True)
        
        # Word cloud
        st.subheader("☁️ Entity Word Cloud")
        wordcloud_fig = visualizer.create_entity_wordcloud(analysis['entities'])
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)
        
        # Detailed entity table
        st.subheader("📋 Detailed Entity Analysis")
        if analysis['entities']:
            df = pd.DataFrame(analysis['entities'])
            st.dataframe(df, use_container_width=True)
        
        # Export options
        st.subheader("💾 Export Options")
        col1, col2 = st.columns(2)

        # Prepare export data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # JSON Export
        with col1:
            # Prepare comprehensive JSON data
            export_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'input_text': text_input,
                'statistics': analysis['stats'],
                'entities': analysis['entities'],
                'relationships': [
                    {
                        'entity1': entity1,
                        'entity2': entity2,
                        'co_occurrence_count': count,
                        'relationship_type': 'co-occurrence'
                    }
                    for entity1, connections in analysis.get('cooccurrence', {}).items()
                    for entity2, count in connections.items()
                    if count > 0
                ],
                'entity_sentiments': analysis['entity_sentiments'],
                'sentences': analysis['sentences']
            }

            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)

            st.download_button(
                label="📄 Download Complete Analysis (JSON)",
                data=json_data,
                file_name=f"entity_analysis_{timestamp}.json",
                mime="application/json",
                help="Download complete analysis including entities, relationships, and statistics"
            )

        # CSV Export
        with col2:
            # Prepare detailed CSV data
            csv_rows = []
            for i, entity in enumerate(analysis['entities']):
                row = {
                    'entity_id': i + 1,
                    'entity_text': entity['text'],
                    'entity_label': entity['label'],
                    'start_position': entity['start'],
                    'end_position': entity['end'],
                    'sentence_id': entity.get('sentence_id', 'N/A'),
                    'dependency_relation': entity.get('dependency', 'N/A'),
                    'head_word': entity.get('head', 'N/A'),
                    'pos_tags': ', '.join(entity.get('pos_context', [])),
                    'sentiment': analysis['entity_sentiments'].get(entity['text'], 'neutral'),
                    'analysis_timestamp': datetime.now().isoformat()
                }
                csv_rows.append(row)

            if csv_rows:
                df = pd.DataFrame(csv_rows)
                csv_data = df.to_csv(index=False)

                st.download_button(
                    label="📊 Download Entity Details (CSV)",
                    data=csv_data,
                    file_name=f"entities_detailed_{timestamp}.csv",
                    mime="text/csv",
                    help="Download detailed entity information in CSV format"
                )
            else:
                st.info("No entities found to export")

        # Additional export options
        st.markdown("---")
        col3, col4 = st.columns(2)

        with col3:
            # Export relationships as CSV
            if analysis.get('cooccurrence'):
                relationships_data = []
                for entity1, connections in analysis.get('cooccurrence', {}).items():
                    for entity2, count in connections.items():
                        if count > 0:
                            relationships_data.append({
                                'entity_1': entity1,
                                'entity_2': entity2,
                                'co_occurrence_count': count,
                                'relationship_type': 'co-occurrence',
                                'analysis_timestamp': datetime.now().isoformat()
                            })

                rel_df = pd.DataFrame(relationships_data)
                rel_csv = rel_df.to_csv(index=False)

                st.download_button(
                    label="🔗 Download Relationships (CSV)",
                    data=rel_csv,
                    file_name=f"entity_relationships_{timestamp}.csv",
                    mime="text/csv",
                    help="Download entity relationships and co-occurrence data"
                )
            else:
                st.info("No relationships found to export")

        with col4:
            # Export summary statistics
            summary_stats = {
                'analysis_summary': [
                    {
                        'metric': 'Total Entities',
                        'value': analysis['stats']['total_entities'],
                        'description': 'Total number of entities found'
                    },
                    {
                        'metric': 'Unique Entities',
                        'value': analysis['stats']['unique_entities'],
                        'description': 'Number of unique entity texts'
                    },
                    {
                        'metric': 'Entity Types',
                        'value': analysis['stats']['entity_types'],
                        'description': 'Number of different entity types'
                    },
                    {
                        'metric': 'Sentences',
                        'value': analysis['stats']['sentences'],
                        'description': 'Number of sentences processed'
                    },
                    {
                        'metric': 'Analysis Timestamp',
                        'value': datetime.now().isoformat(),
                        'description': 'When this analysis was performed'
                    }
                ]
            }

            summary_json = json.dumps(summary_stats, indent=2, ensure_ascii=False)

            st.download_button(
                label="📈 Download Summary (JSON)",
                data=summary_json,
                file_name=f"analysis_summary_{timestamp}.json",
                mime="application/json",
                help="Download analysis summary and statistics"
            )

if __name__ == "__main__":
    create_advanced_visualization_interface()
