import spacy
import pandas as pd
from pathlib import Path
import json
from textblob import TextBlob
from collections import Counter
import argparse

class BatchNERProcessor:
    def __init__(self, model_name='en_core_web_sm'):
        self.nlp = spacy.load(model_name)
    
    def process_text(self, text):
        """Process a single text and extract all information"""
        doc = self.nlp(text)
        
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
        
        # Sentiment analysis
        sentiment = TextBlob(text).sentiment
        
        # Text statistics
        stats = {
            'word_count': len([token for token in doc if not token.is_space]),
            'sentence_count': len(list(doc.sents)),
            'entity_count': len(entities),
            'avg_word_length': sum(len(token.text) for token in doc if not token.is_space) / max(1, len([token for token in doc if not token.is_space]))
        }
        
        return {
            'entities': entities,
            'sentiment': {
                'polarity': sentiment.polarity,
                'subjectivity': sentiment.subjectivity
            },
            'statistics': stats,
            'text_length': len(text)
        }
    
    def process_file(self, file_path):
        """Process a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.process_text(content)
            result['file_name'] = Path(file_path).name
            result['file_path'] = str(file_path)
            
            return result
        except Exception as e:
            return {'error': str(e), 'file_path': str(file_path)}
    
    def process_directory(self, directory_path, file_extensions=None):
        """Process all files in a directory"""
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.csv']
        
        directory = Path(directory_path)
        results = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                print(f"Processing: {file_path}")
                result = self.process_file(file_path)
                results.append(result)
        
        return results
    
    def generate_summary_report(self, results):
        """Generate a comprehensive summary report"""
        total_files = len(results)
        successful_files = len([r for r in results if 'error' not in r])
        
        # Aggregate statistics
        all_entities = []
        all_sentiments = []
        total_words = 0
        
        for result in results:
            if 'error' not in result:
                all_entities.extend([ent['label'] for ent in result['entities']])
                all_sentiments.append(result['sentiment']['polarity'])
                total_words += result['statistics']['word_count']
        
        entity_distribution = Counter(all_entities)
        avg_sentiment = sum(all_sentiments) / max(1, len(all_sentiments))
        
        summary = {
            'total_files_processed': total_files,
            'successful_files': successful_files,
            'failed_files': total_files - successful_files,
            'total_words_processed': total_words,
            'entity_distribution': dict(entity_distribution),
            'average_sentiment': avg_sentiment,
            'most_common_entities': entity_distribution.most_common(10)
        }
        
        return summary
    
    def export_results(self, results, output_format='json', output_file='ner_results'):
        """Export results in various formats"""
        if output_format.lower() == 'json':
            with open(f'{output_file}.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif output_format.lower() == 'csv':
            # Flatten results for CSV
            flattened_data = []
            for result in results:
                if 'error' not in result:
                    base_row = {
                        'file_name': result.get('file_name', ''),
                        'file_path': result.get('file_path', ''),
                        'word_count': result['statistics']['word_count'],
                        'sentence_count': result['statistics']['sentence_count'],
                        'entity_count': result['statistics']['entity_count'],
                        'sentiment_polarity': result['sentiment']['polarity'],
                        'sentiment_subjectivity': result['sentiment']['subjectivity']
                    }
                    
                    if result['entities']:
                        for entity in result['entities']:
                            row = base_row.copy()
                            row.update({
                                'entity_text': entity['text'],
                                'entity_label': entity['label'],
                                'entity_description': entity['description']
                            })
                            flattened_data.append(row)
                    else:
                        flattened_data.append(base_row)
            
            df = pd.DataFrame(flattened_data)
            df.to_csv(f'{output_file}.csv', index=False)
        
        print(f"Results exported to {output_file}.{output_format}")

def main():
    parser = argparse.ArgumentParser(description='Batch NER Processing Tool')
    parser.add_argument('input_path', help='Input file or directory path')
    parser.add_argument('--output', '-o', default='ner_results', help='Output file name (without extension)')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('--extensions', nargs='+', default=['.txt', '.md'], help='File extensions to process')
    
    args = parser.parse_args()
    
    processor = BatchNERProcessor()
    
    input_path = Path(args.input_path)
    
    if input_path.is_file():
        results = [processor.process_file(input_path)]
    elif input_path.is_dir():
        results = processor.process_directory(input_path, args.extensions)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return
    
    # Generate summary
    summary = processor.generate_summary_report(results)
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Files processed: {summary['total_files_processed']}")
    print(f"Successful: {summary['successful_files']}")
    print(f"Failed: {summary['failed_files']}")
    print(f"Total words: {summary['total_words_processed']}")
    print(f"Average sentiment: {summary['average_sentiment']:.2f}")
    print(f"Most common entities: {summary['most_common_entities'][:5]}")
    
    # Export results
    processor.export_results(results, args.format, args.output)
    
    # Export summary
    with open(f'{args.output}_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
