# Deploy Frontend to Vercel
Write-Host "🎨 Deploying Frontend to Vercel..." -ForegroundColor Cyan

# Check if vercel CLI is installed
$vercelExists = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelExists) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Navigate to frontend directory
Set-Location -Path "frontend"

# Login to Vercel
Write-Host "📝 Logging in to Vercel..." -ForegroundColor Cyan
vercel login

# Deploy to production
Write-Host "🚀 Deploying frontend to production..." -ForegroundColor Green
vercel --prod

# Return to root directory
Set-Location -Path ".."

Write-Host ""
Write-Host "✅ Frontend deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Next steps:" -ForegroundColor Yellow
Write-Host "   1. Note your frontend URL (e.g., https://your-app.vercel.app)" -ForegroundColor White
Write-Host "   2. Deploy backend separately" -ForegroundColor White
Write-Host "   3. Update VITE_API_URL in frontend environment variables" -ForegroundColor White
