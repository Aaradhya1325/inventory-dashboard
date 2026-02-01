"""
Vercel Serverless Function Entry Point for FastAPI

This file adapts the FastAPI application to work as a Vercel serverless function.
Note: This is a basic adapter. Some features like WebSockets and background tasks
may have limitations in serverless environments.
"""

from app.main import app

# Vercel expects a variable named 'app' or a handler function
# The FastAPI app instance will be used directly
handler = app
