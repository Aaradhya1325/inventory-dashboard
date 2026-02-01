"""
Vercel Serverless Function Entry Point for FastAPI
"""

import sys
from pathlib import Path

# Add parent directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now import from app.main
from app.main import app

# Vercel handler
handler = app
