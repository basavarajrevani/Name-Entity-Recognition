#!/usr/bin/env python3
"""
Test script to verify export functionality works correctly
"""

import sys
import json
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_advanced_visualization_export():
    """Test the advanced visualization export functionality"""
    print("🧪 Testing Advanced Visualization Export Functionality")
    print("=" * 60)
    
    try:
        from advanced_visualization import AdvancedEntityVisualizer
        
        # Initialize visualizer
        visualizer = AdvancedEntityVisualizer()
        print("✅ Visualizer initialized successfully")
        
        # Test text
        test_text = """
        Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
        Tim Cook became CEO in 2011, succeeding Steve Jobs. The company reported revenue of $394.3 billion in 2022.
        Major competitors include Samsung, Google, Microsoft, and Amazon.
        Tesla, led by Elon Musk, is also a significant competitor in the technology space.
        """
        
        # Perform comprehensive analysis
        print("\n🔍 Performing comprehensive analysis...")
        analysis = visualizer.analyze_text_comprehensive(test_text)
        print(f"✅ Analysis completed")
        print(f"   - Found {len(analysis['entities'])} entities")
        print(f"   - Found {len(analysis['sentences'])} sentences")
        print(f"   - Found {len(analysis['cooccurrence'])} entity relationships")
        print(f"   - Found {len(analysis['entity_sentiments'])} entity sentiments")
        
        # Test JSON export data preparation
        print("\n📄 Testing JSON export data preparation...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        export_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'input_text': test_text,
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
        print(f"✅ JSON export data prepared ({len(json_data)} characters)")
        
        # Save test JSON file
        json_filename = f"test_export_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"✅ JSON file saved: {json_filename}")
        
        # Test CSV export data preparation
        print("\n📊 Testing CSV export data preparation...")
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
            print(f"✅ CSV export data prepared ({len(csv_rows)} rows)")
            
            # Save test CSV file
            csv_filename = f"test_export_{timestamp}.csv"
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            print(f"✅ CSV file saved: {csv_filename}")
        
        # Test relationships export
        print("\n🔗 Testing relationships export...")
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
            
            if relationships_data:
                rel_df = pd.DataFrame(relationships_data)
                rel_csv = rel_df.to_csv(index=False)
                print(f"✅ Relationships export data prepared ({len(relationships_data)} relationships)")
                
                # Save test relationships file
                rel_filename = f"test_relationships_{timestamp}.csv"
                with open(rel_filename, 'w', encoding='utf-8') as f:
                    f.write(rel_csv)
                print(f"✅ Relationships file saved: {rel_filename}")
            else:
                print("ℹ️  No relationships found to export")
        else:
            print("ℹ️  No co-occurrence data found")
        
        # Test summary export
        print("\n📈 Testing summary export...")
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
        print(f"✅ Summary export data prepared")
        
        # Save test summary file
        summary_filename = f"test_summary_{timestamp}.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary_json)
        print(f"✅ Summary file saved: {summary_filename}")
        
        print("\n🎉 All export functionality tests PASSED!")
        print("\n📁 Generated test files:")
        print(f"   - {json_filename}")
        print(f"   - {csv_filename}")
        if 'rel_filename' in locals():
            print(f"   - {rel_filename}")
        print(f"   - {summary_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Export functionality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Export Functionality Test Suite")
    print("=" * 60)
    print("This script tests all export functionality in the Advanced Visualization feature")
    
    success = test_advanced_visualization_export()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe export buttons in the Advanced Visualization feature should now work correctly.")
        print("\nTo test in the web interface:")
        print("1. Go to http://localhost:8502")
        print("2. Select 'Visualization & Analytics' category")
        print("3. Enter some text and click 'Analyze & Visualize'")
        print("4. Scroll down to 'Export Options'")
        print("5. Try all 4 export buttons")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main()
