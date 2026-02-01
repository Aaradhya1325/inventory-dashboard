# Separate Deployment Guide - Frontend & Backend

This guide covers deploying the frontend and backend as separate Vercel projects.

## 📋 Prerequisites

- Vercel account (https://vercel.com)
- Vercel CLI installed: `npm install -g vercel`
- Git repository pushed to GitHub/GitLab/Bitbucket

---

## 🎨 Frontend Deployment

### Option 1: Vercel Dashboard

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New Project"**
3. **Import your repository**
4. **Configure Project**:
   - **Project Name**: `inventory-dashboard-frontend`
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Environment Variables** (Settings > Environment Variables):
   ```
   VITE_API_URL=https://your-backend.vercel.app
   ```
   ⚠️ Add this after deploying the backend

6. **Click "Deploy"**

### Option 2: Vercel CLI

```powershell
# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? **inventory-dashboard-frontend**
- In which directory? **./** (already in frontend)
- Override settings? **N**

### Frontend URL
After deployment, you'll get a URL like:
```
https://inventory-dashboard-frontend.vercel.app
```

---

## ⚙️ Backend Deployment

### ⚠️ Important Backend Considerations

**Vercel Serverless Limitations:**
- **WebSockets**: Not supported in serverless functions
- **Background Tasks**: Limited execution time (10s hobby, 60s pro)
- **Database**: Needs external database (not SQLite)
- **Cold Starts**: First request may be slow

**Recommended Alternatives for Backend:**
1. **Railway** (https://railway.app) - Best for full FastAPI with WebSockets
2. **Render** (https://render.com) - Good Python support
3. **Fly.io** (https://fly.io) - Persistent connections support

### If Using Vercel for Backend (Limited Features)

⚠️ **Note**: This will NOT support WebSockets. Use Railway instead for full functionality.

#### Option 1: Vercel Dashboard

1. **Go to Vercel Dashboard**
2. **Click "Add New Project"**
3. **Import the same repository**
4. **Configure Project**:
   - **Project Name**: `inventory-dashboard-backend`
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: `pip install -r requirements.txt`

5. **Environment Variables**:
   ```
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   DATABASE_URL=your_database_url
   CORS_ORIGINS=https://inventory-dashboard-frontend.vercel.app
   ```

6. **Click "Deploy"**

#### Option 2: Vercel CLI

```powershell
# Navigate to backend directory
cd backend

# Login to Vercel (if not already)
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? **inventory-dashboard-backend**
- In which directory? **./** (already in backend)
- Override settings? **N**

### Backend URL
After deployment, you'll get a URL like:
```
https://inventory-dashboard-backend.vercel.app
```

---

## 🔗 Link Frontend to Backend

### Step 1: Update Frontend Environment Variable

1. Go to **Frontend Vercel Project** > Settings > Environment Variables
2. Add/Update:
   ```
   VITE_API_URL=https://inventory-dashboard-backend.vercel.app
   ```
3. Redeploy frontend: Deployments > Latest > "..." > Redeploy

### Step 2: Update Backend CORS Settings

Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://inventory-dashboard-frontend.vercel.app",  # Your frontend URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push changes to trigger redeployment.

---

## 🚂 Alternative: Deploy Backend on Railway (Recommended)

Railway supports full FastAPI features including WebSockets.

### Steps:

1. **Go to Railway**: https://railway.app
2. **Sign in with GitHub**
3. **New Project** > **Deploy from GitHub repo**
4. **Select your repository**
5. **Configure**:
   - **Root Directory**: `backend`
   - Railway auto-detects Dockerfile
6. **Add Environment Variables**:
   ```
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   DATABASE_URL=your_database_url
   CORS_ORIGINS=https://inventory-dashboard-frontend.vercel.app
   ```
7. **Deploy**

Railway will give you a URL like: `https://your-app.railway.app`

Update frontend's `VITE_API_URL` to use this Railway URL.

---

## 📝 Quick Reference

### Deploy Frontend Only
```powershell
cd frontend
vercel --prod
```

### Deploy Backend Only
```powershell
cd backend
vercel --prod
```

### Update Environment Variables
```powershell
# Using Vercel CLI
vercel env add VITE_API_URL production
# Enter value: https://your-backend.vercel.app
```

---

## 🔍 Troubleshooting

### Frontend Build Fails
```powershell
# Test build locally
cd frontend
npm install
npm run build
```

### Backend Import Errors
- Ensure `requirements.txt` has all dependencies
- Check Python version compatibility (Vercel uses Python 3.9)

### CORS Errors
- Verify frontend URL is in backend's CORS origins
- Check that VITE_API_URL in frontend matches backend URL
- Clear browser cache

### WebSocket Not Working
- Vercel serverless doesn't support WebSockets
- Deploy backend to Railway/Render instead

---

## 🎯 Production Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed (Railway recommended, or Vercel)
- [ ] Database set up (if using PostgreSQL/MySQL)
- [ ] Frontend VITE_API_URL points to backend
- [ ] Backend CORS includes frontend URL
- [ ] Test all API endpoints
- [ ] Test WebSocket connection (if using Railway)
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/logging

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel CLI Docs**: https://vercel.com/docs/cli
- **Railway**: https://railway.app
- **Render**: https://render.com

---

## 💡 Tips

1. **Preview Deployments**: Every git push creates a preview deployment
2. **Production Deployments**: Only main/master branch deploys to production
3. **Environment Variables**: Set separately for Production, Preview, and Development
4. **Logs**: Check deployment logs in Vercel dashboard for errors
5. **Custom Domains**: Add in Project Settings > Domains
