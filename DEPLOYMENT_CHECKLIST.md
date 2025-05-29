# 🚀 Deployment Checklist

Follow this checklist to deploy your Vehicle Parking App to production.

## ✅ Pre-Deployment Preparation

- [ ] **Git Installed**: Verify `git --version` works
- [ ] **GitHub Account**: Have GitHub account ready
- [ ] **Google Cloud Account**: Set up with billing enabled
- [ ] **Netlify Account**: Create free account
- [ ] **MongoDB Atlas Account**: Create free account

## 📤 Step 1: Upload to GitHub

- [ ] Run `deploy.bat` to initialize Git repository
- [ ] Go to [GitHub.com](https://github.com) → "New repository"
- [ ] Repository name: `vehicle-parking-app`
- [ ] Description: `A modern vehicle parking management system`
- [ ] Set to Public (recommended)
- [ ] **DO NOT** initialize with README
- [ ] Copy repository URL
- [ ] Connect local repo to GitHub:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/vehicle-parking-app.git
  git branch -M main
  git push -u origin main
  ```

## 🗄️ Step 2: Set Up MongoDB Atlas

- [ ] Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
- [ ] Create free account
- [ ] Create new project: "Vehicle Parking App"
- [ ] Create free cluster: `parking-app-cluster`
- [ ] **Database Access**: Create user `parkingapp` with strong password
- [ ] **Network Access**: Allow access from anywhere (0.0.0.0/0)
- [ ] Get connection string and save it:
  ```
  mongodb+srv://parkingapp:PASSWORD@parking-app-cluster.xxxxx.mongodb.net/parking_app?retryWrites=true&w=majority
  ```

## ☁️ Step 3: Deploy Backend to Google Cloud

- [ ] Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [ ] Verify: `gcloud --version`
- [ ] Login: `gcloud auth login`
- [ ] Create project: `gcloud projects create vehicle-parking-backend`
- [ ] Set project: `gcloud config set project vehicle-parking-backend`
- [ ] Create app: `gcloud app create --region=us-central1`
- [ ] Edit `backend/app.yaml` with your MongoDB connection string
- [ ] Deploy: `cd backend && gcloud app deploy`
- [ ] Test: Visit your Google Cloud URL
- [ ] Save backend URL: `https://vehicle-parking-backend.uc.r.appspot.com`

## 🌐 Step 4: Deploy Frontend to Netlify

- [ ] Edit `frontend/netlify.toml` with your backend URL
- [ ] Go to [Netlify](https://netlify.com) and login
- [ ] "New site from Git" → Choose GitHub
- [ ] Select your `vehicle-parking-app` repository
- [ ] Build settings:
  - Base directory: `frontend`
  - Build command: `npm run build`
  - Publish directory: `frontend/build`
- [ ] Deploy site
- [ ] Test: Visit your Netlify URL
- [ ] Save frontend URL: `https://YOUR-APP.netlify.app`

## 🔧 Step 5: Update CORS Settings

- [ ] Update `backend/app.yaml` with your Netlify URL:
  ```yaml
  CORS_ORIGINS: "https://YOUR-APP.netlify.app"
  ```
- [ ] Redeploy backend: `cd backend && gcloud app deploy`

## ✅ Step 6: Final Testing

- [ ] Visit your frontend URL
- [ ] Test user registration
- [ ] Test admin login: `admin` / `admin123`
- [ ] Create a parking lot (admin)
- [ ] Book a parking spot (user)
- [ ] Release parking spot (user)
- [ ] Export CSV (user)

## 📝 Your Deployment URLs

Fill in these after deployment:

- **Frontend:** https://______________________.netlify.app
- **Backend:** https://vehicle-parking-backend.uc.r.appspot.com
- **GitHub:** https://github.com/YOUR_USERNAME/vehicle-parking-app
- **MongoDB:** mongodb+srv://parkingapp:PASSWORD@parking-app-cluster.xxxxx.mongodb.net/parking_app

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Frontend loads without errors
- ✅ Admin can login and manage parking lots
- ✅ Users can register and book spots
- ✅ Database persists data between sessions
- ✅ No CORS errors in browser console
- ✅ CSV export works
- ✅ Mobile-responsive design works

## 🆘 Need Help?

- **CORS Issues**: Check `backend/app.yaml` CORS_ORIGINS setting
- **Database Issues**: Verify MongoDB Atlas connection string
- **Build Failures**: Check Netlify build logs
- **Backend Errors**: Check Google Cloud App Engine logs

## 🔄 Making Updates

**Frontend Updates:**
```bash
git add .
git commit -m "Update frontend"
git push origin main
# Netlify auto-deploys
```

**Backend Updates:**
```bash
git add .
git commit -m "Update backend"
git push origin main
cd backend
gcloud app deploy
```

---

🎉 **You're all set!** Your Vehicle Parking App is now live and accessible worldwide! 