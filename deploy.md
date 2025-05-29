# Deployment Guide

This guide will help you deploy your Vehicle Parking App to GitHub, Google Cloud, and Netlify.

## 📋 Prerequisites

1. **Git** installed locally
2. **GitHub account** 
3. **Google Cloud account** with billing enabled
4. **Netlify account**
5. **MongoDB Atlas account** (free tier available)

## 🚀 Step 1: Upload to GitHub

### 1.1 Initialize Git Repository

```bash
# Navigate to your project root
cd "C:\Users\qatty\Downloads\New folder (33)"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Vehicle Parking App with MongoDB"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub](https://github.com) and login
2. Click "New repository" (green button)
3. Repository name: `vehicle-parking-app`
4. Description: `A modern vehicle parking management system with MongoDB backend and React frontend`
5. Set to **Public** (or Private if you prefer)
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

### 1.3 Connect and Push to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/vehicle-parking-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🗄️ Step 2: Set Up MongoDB Atlas (Database)

### 2.1 Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for free account
3. Create a new project: "Vehicle Parking App"
4. Choose "Build a Database" → "Shared" (Free tier)
5. Choose cloud provider and region (closest to you)
6. Cluster name: `parking-app-cluster`
7. Click "Create Cluster"

### 2.2 Configure Database Access

1. **Database Access**:
   - Click "Database Access" in left sidebar
   - Click "Add New Database User"
   - Authentication Method: Password
   - Username: `parkingapp`
   - Password: Generate strong password (save it!)
   - Database User Privileges: "Read and write to any database"
   - Click "Add User"

2. **Network Access**:
   - Click "Network Access" in left sidebar
   - Click "Add IP Address"
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

### 2.3 Get Connection String

1. Go to "Database" → "Connect" on your cluster
2. Choose "Connect your application"
3. Driver: Python, Version: 3.6 or later
4. Copy the connection string (looks like):
   ```
   mongodb+srv://parkingapp:<password>@parking-app-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add database name at the end: `/parking_app`

**Final connection string:**
```
mongodb+srv://parkingapp:YOUR_PASSWORD@parking-app-cluster.xxxxx.mongodb.net/parking_app?retryWrites=true&w=majority
```

## ☁️ Step 3: Deploy Backend to Google Cloud

### 3.1 Install Google Cloud SDK

1. Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Install and restart your terminal
3. Run: `gcloud --version` to verify

### 3.2 Set Up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create new project (replace YOUR_PROJECT_ID with unique name)
gcloud projects create vehicle-parking-backend --name="Vehicle Parking Backend"

# Set current project
gcloud config set project vehicle-parking-backend

# Enable App Engine
gcloud app create --region=us-central1

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3.3 Update Backend Configuration

1. Edit `backend/app.yaml`:
   ```yaml
   env_variables:
     SECRET_KEY: "your-unique-secret-key-here"
     JWT_SECRET_KEY: "your-unique-jwt-secret-here"
     MONGODB_URI: "your-mongodb-atlas-connection-string-here"
     CORS_ORIGINS: "https://your-frontend-domain.netlify.app"
   ```

### 3.4 Deploy Backend

```bash
# Navigate to backend directory
cd backend

# Deploy to Google Cloud
gcloud app deploy

# View your deployed app
gcloud app browse
```

**Your backend will be available at:** `https://vehicle-parking-backend.uc.r.appspot.com`

## 🌐 Step 4: Deploy Frontend to Netlify

### 4.1 Prepare Frontend

1. Edit `frontend/netlify.toml` and replace with your actual backend URL:
   ```toml
   [build.environment]
     REACT_APP_API_URL = "https://vehicle-parking-backend.uc.r.appspot.com"
   ```

### 4.2 Deploy to Netlify

**Option A: GitHub Integration (Recommended)**

1. Go to [Netlify](https://netlify.com) and login
2. Click "New site from Git"
3. Choose "GitHub" and authorize Netlify
4. Select your `vehicle-parking-app` repository
5. Configure build settings:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/build`
6. Click "Deploy site"

**Option B: Manual Deploy**

```bash
# Navigate to frontend
cd frontend

# Install Netlify CLI
npm install -g netlify-cli

# Build the app
npm run build

# Deploy
netlify deploy --prod --dir=build
```

### 4.3 Update CORS Settings

After getting your Netlify URL (e.g., `https://amazing-app-name.netlify.app`):

1. Update `backend/app.yaml`:
   ```yaml
   env_variables:
     CORS_ORIGINS: "https://amazing-app-name.netlify.app"
   ```

2. Redeploy backend:
   ```bash
   cd backend
   gcloud app deploy
   ```

## 🔄 Step 5: Initialize Database

### 5.1 Run Database Setup

```bash
# Access your deployed backend
curl https://vehicle-parking-backend.uc.r.appspot.com/health

# The first request will automatically initialize the database
# Visit your frontend to complete setup
```

## ✅ Step 6: Test Deployment

### 6.1 Test Frontend
1. Visit your Netlify URL
2. Register a new user
3. Login with admin credentials: `admin` / `admin123`

### 6.2 Test Backend API
```bash
# Test health endpoint
curl https://vehicle-parking-backend.uc.r.appspot.com/health

# Test login
curl -X POST https://vehicle-parking-backend.uc.r.appspot.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Ensure CORS_ORIGINS in app.yaml matches your Netlify URL
   - Redeploy backend after updating

2. **Database Connection Issues:**
   - Verify MongoDB Atlas connection string
   - Check network access settings (allow 0.0.0.0/0)
   - Ensure password is correct in connection string

3. **Frontend Not Loading:**
   - Check Netlify build logs
   - Verify REACT_APP_API_URL in netlify.toml
   - Ensure backend is deployed and accessible

4. **Google Cloud Deployment Fails:**
   - Check app.yaml syntax
   - Ensure billing is enabled on Google Cloud
   - Verify all required APIs are enabled

## 📱 Access Your Deployed App

- **Frontend:** `https://your-app-name.netlify.app`
- **Backend API:** `https://vehicle-parking-backend.uc.r.appspot.com`
- **Admin Login:** `admin` / `admin123`

## 🔄 Making Updates

### Update Frontend
```bash
git add .
git commit -m "Update frontend"
git push origin main
# Netlify will auto-deploy
```

### Update Backend
```bash
git add .
git commit -m "Update backend"
git push origin main

cd backend
gcloud app deploy
```

## 💰 Cost Considerations

- **MongoDB Atlas:** Free tier (512MB storage)
- **Google Cloud:** Free tier ($300 credit for new users)
- **Netlify:** Free tier (100GB bandwidth/month)

**Estimated monthly cost after free tiers:** $0-10 for low traffic

---

🎉 **Congratulations!** Your Vehicle Parking App is now deployed and accessible worldwide! 