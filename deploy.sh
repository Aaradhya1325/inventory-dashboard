#!/bin/bash

# Vercel Deployment Script
echo "🚀 Deploying to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null
then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel
echo "📝 Logging in to Vercel..."
vercel login

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo "✅ Deployment complete!"
echo "📱 Your app is now live on Vercel"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Deploy your backend separately (Railway, Render, etc.)"
echo "   2. Update VITE_API_URL in Vercel environment variables"
echo "   3. Update CORS settings in your backend with the Vercel URL"
