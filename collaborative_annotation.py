import streamlit as st
import spacy
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import pandas as pd
from dataclasses import dataclass, asdict
import uuid

@dataclass
class Annotation:
    id: str
    text: str
    start: int
    end: int
    label: str
    annotator: str
    timestamp: str
    confidence: float
    notes: str = ""
    status: str = "pending"  # pending, approved, rejected

class CollaborativeAnnotationSystem:
    def __init__(self, db_path="annotations.db"):
        self.nlp = spacy.load('en_core_web_sm')
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for annotations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annotations (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                start_pos INTEGER NOT NULL,
                end_pos INTEGER NOT NULL,
                label TEXT NOT NULL,
                annotator TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence REAL NOT NULL,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                document_id TEXT,
                original_text TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annotation_votes (
                id TEXT PRIMARY KEY,
                annotation_id TEXT NOT NULL,
                voter TEXT NOT NULL,
                vote TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (annotation_id) REFERENCES annotations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_document(self, title: str, content: str, created_by: str) -> str:
        """Save a document for annotation"""
        doc_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (id, title, content, created_by, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, title, content, created_by, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return doc_id
    
    def get_documents(self) -> List[Dict]:
        """Get all documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE status = "active"')
        docs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': doc[0],
                'title': doc[1],
                'content': doc[2],
                'created_by': doc[3],
                'created_at': doc[4]
            }
            for doc in docs
        ]
    
    def save_annotation(self, annotation: Annotation, document_id: str, original_text: str):
        """Save an annotation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO annotations 
            (id, text, start_pos, end_pos, label, annotator, timestamp, confidence, notes, document_id, original_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            annotation.id, annotation.text, annotation.start, annotation.end,
            annotation.label, annotation.annotator, annotation.timestamp,
            annotation.confidence, annotation.notes, document_id, original_text
        ))
        
        conn.commit()
        conn.close()
    
    def get_annotations(self, document_id: str = None) -> List[Annotation]:
        """Get annotations from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute('SELECT * FROM annotations WHERE document_id = ?', (document_id,))
        else:
            cursor.execute('SELECT * FROM annotations')
        
        annotations = cursor.fetchall()
        conn.close()
        
        return [
            Annotation(
                id=ann[0], text=ann[1], start=ann[2], end=ann[3],
                label=ann[4], annotator=ann[5], timestamp=ann[6],
                confidence=ann[7], notes=ann[8] or "", status=ann[9]
            )
            for ann in annotations
        ]
    
    def vote_on_annotation(self, annotation_id: str, voter: str, vote: str):
        """Vote on an annotation (approve/reject)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        vote_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO annotation_votes (id, annotation_id, voter, vote, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (vote_id, annotation_id, voter, vote, datetime.now().isoformat()))
        
        # Update annotation status based on votes
        cursor.execute('''
            SELECT vote, COUNT(*) FROM annotation_votes 
            WHERE annotation_id = ? GROUP BY vote
        ''', (annotation_id,))
        
        vote_counts = dict(cursor.fetchall())
        approvals = vote_counts.get('approve', 0)
        rejections = vote_counts.get('reject', 0)
        
        # Simple majority rule
        if approvals > rejections and approvals >= 2:
            status = 'approved'
        elif rejections > approvals and rejections >= 2:
            status = 'rejected'
        else:
            status = 'pending'
        
        cursor.execute('UPDATE annotations SET status = ? WHERE id = ?', (status, annotation_id))
        
        conn.commit()
        conn.close()
    
    def get_annotation_stats(self) -> Dict:
        """Get annotation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total annotations
        cursor.execute('SELECT COUNT(*) FROM annotations')
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute('SELECT status, COUNT(*) FROM annotations GROUP BY status')
        status_counts = dict(cursor.fetchall())
        
        # By annotator
        cursor.execute('SELECT annotator, COUNT(*) FROM annotations GROUP BY annotator')
        annotator_counts = dict(cursor.fetchall())
        
        # By label
        cursor.execute('SELECT label, COUNT(*) FROM annotations GROUP BY label')
        label_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'by_status': status_counts,
            'by_annotator': annotator_counts,
            'by_label': label_counts
        }
    
    def auto_suggest_entities(self, text: str) -> List[Dict]:
        """Auto-suggest entities using spaCy"""
        doc = self.nlp(text)
        suggestions = []
        
        for ent in doc.ents:
            suggestions.append({
                'text': ent.text,
                'start': ent.start_char,
                'end': ent.end_char,
                'label': ent.label_,
                'confidence': 0.8  # Default confidence for spaCy
            })
        
        return suggestions

def create_annotation_interface():
    """Streamlit interface for collaborative annotation"""
    st.title("🔄 Collaborative Entity Annotation System")
    st.markdown("Real-time collaborative annotation with voting and quality control")
    
    # Initialize system
    if 'annotation_system' not in st.session_state:
        st.session_state.annotation_system = CollaborativeAnnotationSystem()
    
    system = st.session_state.annotation_system
    
    # Sidebar for user info
    st.sidebar.header("👤 Annotator Info")
    annotator_name = st.sidebar.text_input("Your Name", value="Anonymous")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Annotate", "📊 Review", "📈 Statistics", "📚 Documents"])
    
    with tab1:
        st.header("Create New Annotation")
        
        # Document selection or creation
        docs = system.get_documents()
        
        if docs:
            doc_options = {f"{doc['title']} (by {doc['created_by']})": doc['id'] for doc in docs}
            selected_doc = st.selectbox("Select Document", ["Create New"] + list(doc_options.keys()))
            
            if selected_doc != "Create New":
                doc_id = doc_options[selected_doc]
                selected_doc_data = next(doc for doc in docs if doc['id'] == doc_id)
                text_to_annotate = selected_doc_data['content']
                st.text_area("Document Content", value=text_to_annotate, height=200, disabled=True)
            else:
                doc_id = None
                text_to_annotate = st.text_area("Enter text to annotate:", height=200)
                doc_title = st.text_input("Document Title")
                
                if st.button("Save Document") and text_to_annotate and doc_title:
                    doc_id = system.save_document(doc_title, text_to_annotate, annotator_name)
                    st.success(f"Document saved with ID: {doc_id}")
        else:
            text_to_annotate = st.text_area("Enter text to annotate:", height=200)
            doc_title = st.text_input("Document Title")
            doc_id = None
            
            if st.button("Save Document") and text_to_annotate and doc_title:
                doc_id = system.save_document(doc_title, text_to_annotate, annotator_name)
                st.success(f"Document saved with ID: {doc_id}")
        
        if text_to_annotate:
            # Auto-suggestions
            if st.button("🤖 Get AI Suggestions"):
                suggestions = system.auto_suggest_entities(text_to_annotate)
                st.subheader("AI Suggestions")
                
                for i, suggestion in enumerate(suggestions):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{suggestion['text']}** ({suggestion['label']})")
                    with col2:
                        st.write(f"Conf: {suggestion['confidence']:.2f}")
                    with col3:
                        if st.button("✅ Accept", key=f"accept_{i}"):
                            annotation = Annotation(
                                id=str(uuid.uuid4()),
                                text=suggestion['text'],
                                start=suggestion['start'],
                                end=suggestion['end'],
                                label=suggestion['label'],
                                annotator=annotator_name,
                                timestamp=datetime.now().isoformat(),
                                confidence=suggestion['confidence'],
                                notes="Auto-suggested"
                            )
                            if doc_id:
                                system.save_annotation(annotation, doc_id, text_to_annotate)
                                st.success("Annotation saved!")
                    with col4:
                        if st.button("❌ Reject", key=f"reject_{i}"):
                            st.info("Suggestion rejected")
            
            # Manual annotation
            st.subheader("Manual Annotation")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                entity_text = st.text_input("Entity Text")
                entity_label = st.selectbox("Entity Label", 
                    ["PERSON", "ORG", "GPE", "MONEY", "DATE", "TIME", "PERCENT", "CUSTOM"])
                if entity_label == "CUSTOM":
                    entity_label = st.text_input("Custom Label")
            
            with col2:
                start_pos = st.number_input("Start Position", min_value=0, value=0)
                end_pos = st.number_input("End Position", min_value=0, value=0)
                confidence = st.slider("Confidence", 0.0, 1.0, 0.8)
                notes = st.text_area("Notes", height=100)
            
            if st.button("💾 Save Annotation") and entity_text and doc_id:
                annotation = Annotation(
                    id=str(uuid.uuid4()),
                    text=entity_text,
                    start=start_pos,
                    end=end_pos,
                    label=entity_label,
                    annotator=annotator_name,
                    timestamp=datetime.now().isoformat(),
                    confidence=confidence,
                    notes=notes
                )
                system.save_annotation(annotation, doc_id, text_to_annotate)
                st.success("Annotation saved!")
    
    with tab2:
        st.header("Review Annotations")
        
        annotations = system.get_annotations()
        
        if annotations:
            for annotation in annotations:
                with st.expander(f"{annotation.text} ({annotation.label}) - {annotation.status}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Text:** {annotation.text}")
                        st.write(f"**Label:** {annotation.label}")
                        st.write(f"**Annotator:** {annotation.annotator}")
                        st.write(f"**Confidence:** {annotation.confidence}")
                        if annotation.notes:
                            st.write(f"**Notes:** {annotation.notes}")
                    
                    with col2:
                        if st.button("👍 Approve", key=f"approve_{annotation.id}"):
                            system.vote_on_annotation(annotation.id, annotator_name, "approve")
                            st.success("Vote recorded!")
                    
                    with col3:
                        if st.button("👎 Reject", key=f"reject_{annotation.id}"):
                            system.vote_on_annotation(annotation.id, annotator_name, "reject")
                            st.success("Vote recorded!")
        else:
            st.info("No annotations found")
    
    with tab3:
        st.header("Annotation Statistics")
        
        stats = system.get_annotation_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Annotations", stats['total'])
        
        with col2:
            approved = stats['by_status'].get('approved', 0)
            st.metric("Approved", approved)
        
        with col3:
            pending = stats['by_status'].get('pending', 0)
            st.metric("Pending Review", pending)
        
        # Charts
        if stats['by_label']:
            fig = go.Figure(data=[go.Bar(
                x=list(stats['by_label'].keys()),
                y=list(stats['by_label'].values())
            )])
            fig.update_layout(title="Annotations by Entity Type")
            st.plotly_chart(fig, use_container_width=True)
        
        if stats['by_annotator']:
            fig = go.Figure(data=[go.Pie(
                labels=list(stats['by_annotator'].keys()),
                values=list(stats['by_annotator'].values())
            )])
            fig.update_layout(title="Annotations by Annotator")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Document Management")
        
        docs = system.get_documents()
        
        if docs:
            for doc in docs:
                with st.expander(f"{doc['title']} (by {doc['created_by']})"):
                    st.write(f"**Created:** {doc['created_at']}")
                    st.write(f"**Content Preview:** {doc['content'][:200]}...")
                    
                    # Show annotation count for this document
                    doc_annotations = system.get_annotations(doc['id'])
                    st.write(f"**Annotations:** {len(doc_annotations)}")
        else:
            st.info("No documents found")

if __name__ == "__main__":
    create_annotation_interface()
