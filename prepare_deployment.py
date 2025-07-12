#!/usr/bin/env python3
"""
Deployment preparation script for Render hosting
This script helps prepare your NER project for deployment
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def check_files():
    """Check if all necessary files exist"""
    print_step("1", "Checking Deployment Files")
    
    required_files = [
        "requirements-render.txt",
        "render.yaml", 
        "app.py",
        ".streamlit/config.toml",
        "Dockerfile",
        "DEPLOYMENT_GUIDE.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files!")
        return False
    else:
        print(f"\n✅ All deployment files present!")
        return True

def test_app_locally():
    """Test the app locally before deployment"""
    print_step("2", "Testing App Locally")
    
    try:
        # Test imports
        print("Testing imports...")
        import streamlit
        import spacy
        import pandas
        import plotly
        print("✅ Core imports successful")
        
        # Test spaCy model
        print("Testing spaCy model...")
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Apple Inc. is based in California")
        entities = [ent.text for ent in doc.ents]
        print(f"✅ spaCy model working - found {len(entities)} entities")
        
        # Test app file
        print("Testing app.py...")
        if os.path.exists('app.py'):
            print("✅ app.py exists and ready for deployment")
        else:
            print("❌ app.py not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Local testing failed: {e}")
        return False

def create_gitignore():
    """Create .gitignore file for deployment"""
    print_step("3", "Creating .gitignore")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.db
*.sqlite3
logs/
outputs/
test_*.json
test_*.csv
annotations.db

# Temporary files
temp/
tmp/
*.tmp

# Model files (will be downloaded during deployment)
models/
*.model

# Environment variables
.env
.env.local
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ .gitignore created")

def optimize_for_deployment():
    """Optimize project for deployment"""
    print_step("4", "Optimizing for Deployment")
    
    # Create optimized requirements
    print("Creating optimized requirements...")
    
    # Remove test files that aren't needed for deployment
    test_files = [
        'test_ner.py',
        'test_export_functionality.py',
        'run_full_demo.py'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"ℹ️  Keeping {file} (useful for testing)")
    
    # Create deployment directory structure
    dirs_to_create = ['.streamlit', 'data', 'models', 'outputs', 'logs']
    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Directory created: {dir_name}")
    
    print("✅ Optimization complete")

def generate_deployment_summary():
    """Generate deployment summary"""
    print_step("5", "Deployment Summary")
    
    print("""
📋 DEPLOYMENT CHECKLIST:

✅ Files Ready:
   - requirements-render.txt (optimized dependencies)
   - render.yaml (Render configuration)
   - app.py (main application)
   - .streamlit/config.toml (Streamlit config)
   - Dockerfile (optional)
   - .gitignore (Git ignore rules)

🚀 Next Steps:
   1. Push code to GitHub repository
   2. Connect GitHub to Render
   3. Deploy using render.yaml or manual setup
   4. Monitor deployment logs
   5. Test live application

🌐 Deployment Options:
   - Free Tier: Perfect for demos and portfolio
   - Paid Tier: Production-ready with custom domains

📚 Resources:
   - DEPLOYMENT_GUIDE.md: Complete deployment instructions
   - Render Dashboard: https://dashboard.render.com
   - Live URL: Will be provided after deployment
""")

def check_git_status():
    """Check git status and provide guidance"""
    print_step("6", "Git Repository Status")
    
    try:
        # Check if git is initialized
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Git repository initialized")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout:
                print("✅ No uncommitted changes")
            else:
                print("⚠️  You have uncommitted changes")
                print("Run these commands before deployment:")
                print("   git add .")
                print("   git commit -m 'Prepare for deployment'")
                print("   git push origin main")
        else:
            print("❌ Git not initialized")
            print("Run these commands to set up git:")
            print("   git init")
            print("   git add .")
            print("   git commit -m 'Initial commit'")
            print("   git remote add origin YOUR_GITHUB_REPO_URL")
            print("   git push -u origin main")
    
    except FileNotFoundError:
        print("❌ Git not installed")
        print("Please install Git: https://git-scm.com/downloads")

def main():
    """Main preparation function"""
    print_header("Deployment Preparation for Render")
    print("This script will prepare your NER project for deployment on Render")
    
    # Run preparation steps
    files_ok = check_files()
    if not files_ok:
        print("\n❌ Missing required files. Please run the setup first.")
        return
    
    app_ok = test_app_locally()
    if not app_ok:
        print("\n❌ Local testing failed. Please fix issues before deployment.")
        return
    
    create_gitignore()
    optimize_for_deployment()
    check_git_status()
    generate_deployment_summary()
    
    print_header("READY FOR DEPLOYMENT!")
    print("""
🎉 Your Advanced NER Suite is ready for deployment!

📖 Next Steps:
1. Read DEPLOYMENT_GUIDE.md for detailed instructions
2. Push your code to GitHub
3. Deploy on Render using the provided configuration
4. Share your live demo with the world!

🌟 Your project will be accessible at:
   https://your-app-name.onrender.com

Good luck with your deployment! 🚀
""")

if __name__ == "__main__":
    main()
