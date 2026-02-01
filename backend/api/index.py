"""
Vercel Serverless Function Entry Point for FastAPI
"""

import sys
from pathlib import Path

# Add parent directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from main import app

# Import Mangum adapter for AWS Lambda/Vercel
from mangum import Mangum

# Create the Vercel handler
handler = Mangum(app, lifespan="off")
