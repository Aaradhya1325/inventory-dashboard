# Quick Start - Deploy to Vercel

## 🎯 Simple Deployment Steps

### Step 1: Install Vercel CLI
```powershell
npm install -g vercel
```

### Step 2: Login
```powershell
vercel login
```

### Step 3: Deploy
```powershell
vercel --prod
```

Or simply run:
```powershell
.\deploy.ps1
```

### Step 4: Configure Build Settings in Vercel Dashboard

When prompted or in the Vercel dashboard:
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 5: Deploy Backend Separately

Your backend needs to be deployed on a platform that supports Python/FastAPI:
- **Railway** (Recommended): https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io

### Step 6: Update Environment Variables

In Vercel dashboard (Settings > Environment Variables):
```
VITE_API_URL=https://your-backend-url.railway.app
```

## 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions and troubleshooting.

## ⚡ Important Notes

1. **Frontend only on Vercel**: Your React frontend will be deployed on Vercel
2. **Backend separately**: Deploy your FastAPI backend on Railway/Render
3. **Update CORS**: Add your Vercel URL to backend CORS settings
4. **Environment variables**: Set VITE_API_URL in Vercel to point to your backend

## 🔗 Useful Links

- Vercel Dashboard: https://vercel.com/dashboard
- Vercel Docs: https://vercel.com/docs
- Railway: https://railway.app (for backend)
