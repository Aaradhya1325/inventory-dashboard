# Deploy Backend to Vercel
Write-Host "⚙️  Deploying Backend to Vercel..." -ForegroundColor Cyan
Write-Host ""

# Check if vercel CLI is installed
$vercelExists = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelExists) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Navigate to backend directory
Set-Location -Path "backend"

# Login to Vercel
Write-Host "📝 Logging in to Vercel..." -ForegroundColor Cyan
vercel login

# Deploy to production
Write-Host "🚀 Deploying backend to production..." -ForegroundColor Green
vercel --prod

# Return to root directory
Set-Location -Path ".."

Write-Host ""
Write-Host "✅ Backend deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Next steps:" -ForegroundColor Yellow
Write-Host "   1. Note your backend URL (e.g., https://your-backend.vercel.app)" -ForegroundColor White
Write-Host "   2. Update VITE_API_URL in frontend Vercel environment variables" -ForegroundColor White
Write-Host "   3. Update CORS_ORIGINS in backend environment variables" -ForegroundColor White
Write-Host "   4. Redeploy frontend with new environment variable" -ForegroundColor White
