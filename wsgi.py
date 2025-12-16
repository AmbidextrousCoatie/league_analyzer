import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
legacy_v1_path = os.path.join(project_root, 'league_analyzer_v1')

# Add legacy v1 directory to Python path so imports like 'from app' work
sys.path.insert(0, legacy_v1_path)
# Also add project root for any other dependencies
sys.path.insert(0, project_root)

# Import Flask app from legacy v1 location
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 