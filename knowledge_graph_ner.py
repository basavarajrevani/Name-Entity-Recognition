import spacy
import requests
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import streamlit as st
from dataclasses import dataclass
import json

@dataclass
class EntityInfo:
    text: str
    label: str
    wikidata_id: str = None
    description: str = None
    image_url: str = None
    website: str = None
    coordinates: Tuple[float, float] = None
    related_entities: List[str] = None

class KnowledgeGraphNER:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.graph = nx.Graph()
        self.entity_cache = {}
    
    def enrich_entity_with_wikidata(self, entity_text: str, entity_type: str) -> EntityInfo:
        """Enrich entity with Wikidata information"""
        if entity_text in self.entity_cache:
            return self.entity_cache[entity_text]
        
        try:
            # Search Wikidata
            search_url = "https://www.wikidata.org/w/api.php"
            search_params = {
                'action': 'wbsearchentities',
                'search': entity_text,
                'language': 'en',
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(search_url, params=search_params, timeout=5)
            data = response.json()
            
            if data.get('search'):
                item = data['search'][0]
                entity_id = item['id']
                
                # Get detailed information
                detail_params = {
                    'action': 'wbgetentities',
                    'ids': entity_id,
                    'format': 'json',
                    'languages': 'en'
                }
                
                detail_response = requests.get(search_url, params=detail_params, timeout=5)
                detail_data = detail_response.json()
                
                entity_data = detail_data['entities'][entity_id]
                
                # Extract information
                description = entity_data.get('descriptions', {}).get('en', {}).get('value', '')
                
                # Get coordinates if it's a location
                coordinates = None
                if 'P625' in entity_data.get('claims', {}):  # P625 is coordinate location
                    coord_claim = entity_data['claims']['P625'][0]
                    if 'mainsnak' in coord_claim and 'datavalue' in coord_claim['mainsnak']:
                        coord_data = coord_claim['mainsnak']['datavalue']['value']
                        coordinates = (coord_data['latitude'], coord_data['longitude'])
                
                # Get website if available
                website = None
                if 'P856' in entity_data.get('claims', {}):  # P856 is official website
                    website_claim = entity_data['claims']['P856'][0]
                    if 'mainsnak' in website_claim and 'datavalue' in website_claim['mainsnak']:
                        website = website_claim['mainsnak']['datavalue']['value']
                
                entity_info = EntityInfo(
                    text=entity_text,
                    label=entity_type,
                    wikidata_id=entity_id,
                    description=description,
                    website=website,
                    coordinates=coordinates
                )
                
                self.entity_cache[entity_text] = entity_info
                return entity_info
        
        except Exception as e:
            print(f"Error enriching entity {entity_text}: {e}")
        
        # Return basic entity info if enrichment fails
        return EntityInfo(text=entity_text, label=entity_type)
    
    def build_knowledge_graph(self, text: str) -> Dict:
        """Build a knowledge graph from text entities"""
        doc = self.nlp(text)
        entities = []
        
        # Extract and enrich entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT']:  # Focus on key entity types
                enriched_entity = self.enrich_entity_with_wikidata(ent.text, ent.label_)
                entities.append(enriched_entity)
                
                # Add to graph
                self.graph.add_node(
                    ent.text,
                    label=ent.label_,
                    description=enriched_entity.description,
                    wikidata_id=enriched_entity.wikidata_id
                )
        
        # Find relationships between entities (co-occurrence in sentences)
        for sent in doc.sents:
            sent_entities = [ent.text for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT']]
            
            # Add edges between entities in the same sentence
            for i, entity1 in enumerate(sent_entities):
                for entity2 in sent_entities[i+1:]:
                    if self.graph.has_edge(entity1, entity2):
                        self.graph[entity1][entity2]['weight'] += 1
                    else:
                        self.graph.add_edge(entity1, entity2, weight=1, relationship='co-occurrence')
        
        return {
            'entities': entities,
            'graph': self.graph,
            'relationships': list(self.graph.edges(data=True))
        }
    
    def visualize_knowledge_graph(self) -> go.Figure:
        """Create interactive knowledge graph visualization"""
        if not self.graph.nodes():
            return None
        
        # Calculate layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Prepare node traces
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        color_map = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4', 
            'GPE': '#45B7D1',
            'EVENT': '#96CEB4'
        }
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = self.graph.nodes[node]
            label = node_data.get('label', 'UNKNOWN')
            description = node_data.get('description', 'No description available')
            
            node_text.append(f"{node}<br>{label}<br>{description[:100]}...")
            node_color.append(color_map.get(label, '#95A5A6'))
            
            # Node size based on degree (number of connections)
            degree = self.graph.degree(node)
            node_size.append(max(20, degree * 10))
        
        # Prepare edge traces
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Relationships'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_text,
            text=[node.split()[0] for node in self.graph.nodes()],  # Show first word
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            name='Entities'
        ))
        
        fig.update_layout(
            title="Knowledge Graph - Entity Relationships",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Entities connected by co-occurrence in text",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#888', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig

def create_knowledge_graph_interface():
    """Streamlit interface for knowledge graph NER"""
    st.title("🧠 AI-Powered Knowledge Graph NER")
    st.markdown("Extract entities and build intelligent knowledge graphs with real-world data")
    
    # Initialize knowledge graph NER
    if 'kg_ner' not in st.session_state:
        st.session_state.kg_ner = KnowledgeGraphNER()
    
    kg_ner = st.session_state.kg_ner
    
    # Input text
    text_input = st.text_area(
        "Enter text to analyze:",
        placeholder="Enter text about people, organizations, places, or events...",
        height=150
    )
    
    if st.button("🔍 Build Knowledge Graph") and text_input:
        with st.spinner("Building knowledge graph and enriching entities..."):
            result = kg_ner.build_knowledge_graph(text_input)
        
        # Display results
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Enriched Entities")
            for entity in result['entities']:
                with st.expander(f"{entity.text} ({entity.label})"):
                    if entity.description:
                        st.write(f"**Description:** {entity.description}")
                    if entity.website:
                        st.write(f"**Website:** {entity.website}")
                    if entity.coordinates:
                        st.write(f"**Location:** {entity.coordinates[0]:.4f}, {entity.coordinates[1]:.4f}")
                    if entity.wikidata_id:
                        st.write(f"**Wikidata ID:** {entity.wikidata_id}")
        
        with col2:
            st.subheader("🔗 Entity Relationships")
            if result['relationships']:
                for rel in result['relationships'][:10]:  # Show top 10
                    weight = rel[2].get('weight', 1)
                    st.write(f"**{rel[0]}** ↔ **{rel[1]}** (strength: {weight})")
            else:
                st.write("No relationships found")
        
        # Visualize knowledge graph
        st.subheader("🌐 Interactive Knowledge Graph")
        fig = kg_ner.visualize_knowledge_graph()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No entities found to create knowledge graph")

if __name__ == "__main__":
    create_knowledge_graph_interface()
