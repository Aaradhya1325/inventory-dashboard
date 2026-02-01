# Vercel Deployment Guide

## Prerequisites
- A Vercel account (sign up at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)
- Node.js installed locally

## Important Notes

### Frontend Deployment
Your **frontend** will be deployed on Vercel.

### Backend Deployment
⚠️ **Important**: Vercel is optimized for frontend and serverless functions. Your FastAPI backend requires a persistent server, so you'll need to deploy it separately on one of these platforms:
- **Railway** (https://railway.app) - Recommended for Python backends
- **Render** (https://render.com)
- **Fly.io** (https://fly.io)
- **Digital Ocean App Platform**

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Make sure all your changes are committed:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   ```

2. Push to your GitHub repository:
   ```bash
   git push origin main
   ```
   
   If you haven't set up the remote yet:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy Frontend to Vercel

#### Option A: Using Vercel Dashboard (Recommended for beginners)

1. Go to https://vercel.com and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the framework (Vite)
5. Configure the build settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
6. Add Environment Variables (if needed):
   - Click "Environment Variables"
   - Add `VITE_API_URL` = `https://your-backend-url.com` (you'll update this after deploying backend)
7. Click **"Deploy"**

#### Option B: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy from project root:
   ```bash
   vercel
   ```

4. Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - What's your project's name? **inventory-dashboard**
   - In which directory is your code located? **frontend**
   - Override settings? **Y** (if you want to customize)

5. For production deployment:
   ```bash
   vercel --prod
   ```

### Step 3: Deploy Backend (Separate Platform)

#### Recommended: Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will detect the Dockerfile in `/backend`
7. Set the **Root Directory** to `backend`
8. Add environment variables in the Railway dashboard
9. Deploy!

After deployment, Railway will give you a URL like: `https://your-app.railway.app`

### Step 4: Update Frontend Environment

1. Go back to your Vercel project
2. Navigate to **Settings** > **Environment Variables**
3. Add or update:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
4. Redeploy the frontend (Vercel > Deployments > Click "..." > Redeploy)

### Step 5: Update CORS Settings

Update your backend CORS settings to allow your Vercel frontend URL:

In `backend/app/main.py`, update the CORS middleware to include your Vercel URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment Variables

### Frontend (.env in frontend/)
```env
VITE_API_URL=https://your-backend-url.railway.app
```

### Backend (.env in backend/)
```env
DATABASE_URL=your_database_url
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-app.vercel.app
```

## Troubleshooting

### Build Fails
- Check that all dependencies are in `frontend/package.json`
- Verify build command works locally: `cd frontend && npm run build`
- Check Vercel build logs for specific errors

### API Connection Issues
- Verify VITE_API_URL is set correctly in Vercel
- Check backend CORS settings include your Vercel URL
- Ensure backend is running and accessible

### WebSocket Issues
- WebSockets may require additional configuration on some platforms
- Consider using Socket.io as an alternative for better compatibility

## Custom Domain (Optional)

1. In Vercel dashboard, go to **Settings** > **Domains**
2. Add your custom domain
3. Update DNS records as instructed by Vercel
4. Update CORS settings in backend to include custom domain

## Continuous Deployment

Once set up, any push to your main branch will automatically trigger a new deployment on Vercel.

## Useful Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel rm [deployment-url]
```

## Support

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Community: https://github.com/vercel/vercel/discussions
