from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import spacy
from textblob import TextBlob
import uvicorn
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced NER API",
    description="A powerful Named Entity Recognition API with multiple features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
    logger.info("spaCy model loaded successfully")
except OSError:
    logger.error("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
    nlp = None

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str
    include_sentiment: bool = True
    include_pos: bool = False
    include_dependencies: bool = False

class EntityResponse(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float
    description: str

class AnalysisResponse(BaseModel):
    text: str
    entities: List[EntityResponse]
    sentiment: Optional[Dict[str, float]] = None
    statistics: Dict[str, Any]
    processing_time: float
    timestamp: str

class BatchTextInput(BaseModel):
    texts: List[str]
    include_sentiment: bool = True

# API endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Advanced NER API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "Analyze single text",
            "/batch": "Analyze multiple texts",
            "/upload": "Upload and analyze file",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy model not loaded")
    
    return {
        "status": "healthy",
        "model_loaded": nlp is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """Analyze a single text for named entities and other features"""
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy model not loaded")
    
    start_time = datetime.now()
    
    try:
        # Process text with spaCy
        doc = nlp(input_data.text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append(EntityResponse(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=getattr(ent, 'confidence', 1.0),  # spaCy doesn't always provide confidence
                description=spacy.explain(ent.label_) or "Unknown"
            ))
        
        # Calculate statistics
        stats = {
            "word_count": len([token for token in doc if not token.is_space]),
            "sentence_count": len(list(doc.sents)),
            "entity_count": len(entities),
            "unique_entities": len(set(ent.text for ent in entities)),
            "character_count": len(input_data.text)
        }
        
        # Sentiment analysis (optional)
        sentiment = None
        if input_data.include_sentiment:
            blob = TextBlob(input_data.text)
            sentiment = {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity
            }
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            text=input_data.text,
            entities=entities,
            sentiment=sentiment,
            statistics=stats,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/batch")
async def analyze_batch(input_data: BatchTextInput):
    """Analyze multiple texts in batch"""
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy model not loaded")
    
    start_time = datetime.now()
    results = []
    
    try:
        for i, text in enumerate(input_data.texts):
            # Create individual analysis
            individual_input = TextInput(
                text=text,
                include_sentiment=input_data.include_sentiment
            )
            
            # Reuse the analyze_text logic
            result = await analyze_text(individual_input)
            result_dict = result.dict()
            result_dict['batch_index'] = i
            results.append(result_dict)
        
        # Calculate batch statistics
        total_processing_time = (datetime.now() - start_time).total_seconds()
        batch_stats = {
            "total_texts": len(input_data.texts),
            "total_entities": sum(len(r['entities']) for r in results),
            "total_words": sum(r['statistics']['word_count'] for r in results),
            "average_sentiment": sum(r['sentiment']['polarity'] for r in results if r['sentiment']) / len(results) if input_data.include_sentiment else None,
            "total_processing_time": total_processing_time
        }
        
        return {
            "results": results,
            "batch_statistics": batch_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """Upload a text file and analyze its content"""
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy model not loaded")
    
    # Check file type
    if not file.filename.endswith(('.txt', '.md', '.csv')):
        raise HTTPException(status_code=400, detail="Only .txt, .md, and .csv files are supported")
    
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Analyze the text
        input_data = TextInput(text=text, include_sentiment=True)
        result = await analyze_text(input_data)
        
        # Add file information
        result_dict = result.dict()
        result_dict['file_info'] = {
            "filename": file.filename,
            "file_size": len(content),
            "content_type": file.content_type
        }
        
        return result_dict
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8 encoded files.")
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/entities/types")
async def get_entity_types():
    """Get all available entity types and their descriptions"""
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy model not loaded")
    
    # Get all entity labels from the model
    entity_types = {}
    for label in nlp.get_pipe('ner').labels:
        entity_types[label] = spacy.explain(label) or "No description available"
    
    return {
        "entity_types": entity_types,
        "total_types": len(entity_types)
    }

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "ner_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
