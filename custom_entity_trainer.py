import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json
from pathlib import Path

class CustomEntityTrainer:
    def __init__(self, base_model='en_core_web_sm'):
        """Initialize the custom entity trainer"""
        self.nlp = spacy.load(base_model)
        self.training_data = []
        
        # Add NER component if it doesn't exist
        if 'ner' not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe('ner')
        else:
            ner = self.nlp.get_pipe('ner')
        
        self.ner = ner
    
    def add_training_data(self, text, entities):
        """
        Add training data in the format:
        text: "Apple Inc. is a technology company"
        entities: [(0, 10, "COMPANY"), (16, 26, "INDUSTRY")]
        """
        self.training_data.append((text, {"entities": entities}))
    
    def load_training_data_from_file(self, file_path):
        """Load training data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            self.add_training_data(item['text'], item['entities'])
    
    def add_custom_labels(self, labels):
        """Add custom entity labels to the NER component"""
        for label in labels:
            self.ner.add_label(label)
    
    def train_model(self, iterations=30, drop_rate=0.2):
        """Train the model with custom entities"""
        if not self.training_data:
            raise ValueError("No training data available. Add training data first.")
        
        # Disable other pipes during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != 'ner']
        
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.begin_training()
            
            for iteration in range(iterations):
                print(f"Training iteration {iteration + 1}/{iterations}")
                random.shuffle(self.training_data)
                losses = {}
                
                # Create training examples
                examples = []
                for text, annotations in self.training_data:
                    doc = self.nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                
                # Update the model
                batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    self.nlp.update(batch, drop=drop_rate, losses=losses)
                
                print(f"Losses: {losses}")
    
    def save_model(self, output_dir):
        """Save the trained model"""
        output_path = Path(output_dir)
        if not output_path.exists():
            output_path.mkdir(parents=True)
        
        self.nlp.to_disk(output_path)
        print(f"Model saved to {output_path}")
    
    def test_model(self, test_texts):
        """Test the trained model on new texts"""
        results = []
        for text in test_texts:
            doc = self.nlp(text)
            entities = [(ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
            results.append({
                'text': text,
                'entities': entities
            })
        return results

# Example usage and predefined training data
def create_sample_training_data():
    """Create sample training data for custom entities"""
    training_data = [
        # Technology companies
        ("Apple Inc. is a major technology company", [(0, 10, "TECH_COMPANY")]),
        ("Google develops search engines", [(0, 6, "TECH_COMPANY")]),
        ("Microsoft creates software products", [(0, 9, "TECH_COMPANY")]),
        ("Amazon provides cloud services", [(0, 6, "TECH_COMPANY")]),
        
        # Programming languages
        ("Python is a programming language", [(0, 6, "PROGRAMMING_LANG")]),
        ("JavaScript runs in browsers", [(0, 10, "PROGRAMMING_LANG")]),
        ("Java is used for enterprise applications", [(0, 4, "PROGRAMMING_LANG")]),
        ("C++ is a systems programming language", [(0, 3, "PROGRAMMING_LANG")]),
        
        # Software products
        ("Visual Studio Code is an editor", [(0, 18, "SOFTWARE")]),
        ("Photoshop is used for image editing", [(0, 9, "SOFTWARE")]),
        ("Excel handles spreadsheet data", [(0, 5, "SOFTWARE")]),
        ("Chrome is a web browser", [(0, 6, "SOFTWARE")]),
        
        # Cryptocurrencies
        ("Bitcoin is a digital currency", [(0, 7, "CRYPTOCURRENCY")]),
        ("Ethereum supports smart contracts", [(0, 8, "CRYPTOCURRENCY")]),
        ("Dogecoin gained popularity recently", [(0, 8, "CRYPTOCURRENCY")]),
        ("Litecoin is similar to Bitcoin", [(0, 8, "CRYPTOCURRENCY")]),
    ]
    
    return training_data

def main():
    # Initialize trainer
    trainer = CustomEntityTrainer()
    
    # Add custom labels
    custom_labels = ["TECH_COMPANY", "PROGRAMMING_LANG", "SOFTWARE", "CRYPTOCURRENCY"]
    trainer.add_custom_labels(custom_labels)
    
    # Load sample training data
    sample_data = create_sample_training_data()
    for text, entities in sample_data:
        trainer.add_training_data(text, entities['entities'])
    
    print("Starting training...")
    trainer.train_model(iterations=20)
    
    # Test the model
    test_texts = [
        "Facebook is developing new AI technologies",
        "Rust is a systems programming language",
        "Cardano is a blockchain platform",
        "IntelliJ IDEA is a development environment"
    ]
    
    print("\nTesting trained model:")
    results = trainer.test_model(test_texts)
    for result in results:
        print(f"Text: {result['text']}")
        print(f"Entities: {result['entities']}")
        print("-" * 50)
    
    # Save the model
    trainer.save_model("./custom_ner_model")

if __name__ == "__main__":
    main()
