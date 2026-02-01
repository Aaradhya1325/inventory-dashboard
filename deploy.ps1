# Vercel Deployment Script for Windows
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Green

# Check if vercel CLI is installed
$vercelExists = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelExists) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Login to Vercel
Write-Host "📝 Logging in to Vercel..." -ForegroundColor Cyan
vercel login

# Deploy to production
Write-Host "🚀 Deploying to production..." -ForegroundColor Cyan
vercel --prod

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📱 Your app is now live on Vercel" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Don't forget to:" -ForegroundColor Yellow
Write-Host "   1. Deploy your backend separately (Railway, Render, etc.)" -ForegroundColor White
Write-Host "   2. Update VITE_API_URL in Vercel environment variables" -ForegroundColor White
Write-Host "   3. Update CORS settings in your backend with the Vercel URL" -ForegroundColor White
