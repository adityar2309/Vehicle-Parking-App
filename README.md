# Vehicle Parking App

A modern web application for managing vehicle parking reservations with MongoDB backend, React frontend, and role-based access control.

## 🚗 Features

### Admin Features
- **Dashboard**: Overview of parking statistics and recent activity
- **Parking Lot Management**: Create, edit, and delete parking lots
- **User Management**: View and manage registered users
- **Spot Management**: Monitor individual parking spots in real-time
- **Export Management**: Handle CSV export requests and cleanup

### User Features  
- **Dashboard**: Personal parking statistics and current reservations
- **Booking System**: Find and book available parking spots
- **Reservation Management**: View booking history and current reservations
- **CSV Export**: Download parking history as CSV files
- **Real-time Updates**: Live spot availability and booking status

## 🏗️ Architecture

- **Frontend**: React.js with Bootstrap styling
- **Backend**: Flask REST API with JWT authentication
- **Database**: MongoDB with MongoEngine ODM
- **Caching**: Simple in-memory caching (Redis-free)
- **Background Jobs**: Synchronous job execution
- **Email**: SMTP integration for notifications

## 🚀 Live Demo

- **Frontend**: [https://parking-app-frontend.netlify.app](https://parking-app-frontend.netlify.app)
- **Backend API**: [https://parking-app-backend.uc.r.appspot.com](https://parking-app-backend.uc.r.appspot.com)
- **Login Page**: [https://vehicle-parking-app.netlify.app/login](https://vehicle-parking-app.netlify.app/login)

### Demo Credentials
- **Admin**: `username: admin`, `password: admin123`
- **User**: `username: testuser`, `password: password123`

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB 4.4+

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/vehicle-parking-app.git
cd vehicle-parking-app

# Setup (Windows)
setup.bat

# Run application (Windows)
run.bat

# Manual setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

cd ../frontend
npm install
```

### Running the Application
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🌐 Deployment

### Backend Deployment (Google Cloud)

1. **Prepare for Google Cloud**:
   ```bash
   cd backend
   gcloud init
   gcloud app create
   ```

2. **Deploy**:
   ```bash
   gcloud app deploy
   ```

3. **Environment Variables**: Set in Google Cloud Console or app.yaml

### Frontend Deployment (Netlify)

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Netlify**:
   - Connect your GitHub repository to Netlify
   - Set build command: `npm run build`
   - Set publish directory: `build`
   - Configure environment variables

### Database (MongoDB Atlas)

For production, use MongoDB Atlas:
1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Get your connection string
3. Update environment variables:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/parking_app
   ```

## 📁 Project Structure

```
vehicle-parking-app/
├── backend/                 # Flask API server
│   ├── models.py           # MongoDB models
│   ├── auth.py             # Authentication routes
│   ├── admin_routes.py     # Admin endpoints
│   ├── user_routes.py      # User endpoints
│   ├── export_routes.py    # CSV export functionality
│   ├── background_jobs.py  # Background job processing
│   ├── cache_service.py    # Caching layer
│   ├── email_service.py    # Email notifications
│   ├── config.py           # Configuration settings
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── app.yaml            # Google Cloud config
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── netlify.toml        # Netlify config
├── .gitignore              # Git ignore rules
├── setup.bat               # Windows setup script
├── run.bat                 # Windows run script
└── README.md               # This file
```

## 🔧 Configuration

### Backend Environment Variables (.env)
```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MONGODB_URI=mongodb://localhost:27017/parking_app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Frontend Environment Variables
```bash
REACT_APP_API_URL=http://localhost:5000
```

## 🧪 Testing

```bash
# Backend tests
cd backend
python test_app.py

# Test all components
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📊 API Documentation

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/verify` - Verify JWT token

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard data
- `GET /admin/parking-lots` - List all parking lots
- `POST /admin/parking-lots` - Create parking lot
- `PUT /admin/parking-lots/<id>` - Update parking lot
- `DELETE /admin/parking-lots/<id>` - Delete parking lot
- `GET /admin/users` - List all users

### User Endpoints
- `GET /user/dashboard` - User dashboard data
- `GET /user/parking-lots` - Available parking lots
- `POST /user/book-spot` - Book parking spot
- `POST /user/release-spot` - Release parking spot
- `GET /user/reservations` - User's reservations

### Export Endpoints
- `POST /api/export/csv/request` - Request CSV export
- `GET /api/export/csv/status/<job_id>` - Check export status
- `GET /api/export/download/<job_id>` - Download CSV file

## 🔄 Migration from Redis/PostgreSQL

This app was migrated from Redis/PostgreSQL to MongoDB. See `MONGODB_MIGRATION.md` for details.

### Key Changes:
- ✅ MongoDB replaces PostgreSQL
- ✅ Simple in-memory cache replaces Redis  
- ✅ Synchronous jobs replace Celery
- ✅ MongoEngine ODM replaces SQLAlchemy
- ✅ Simplified deployment architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [TESTING_GUIDE.md](TESTING_GUIDE.md) for troubleshooting
- Review [MONGODB_MIGRATION.md](MONGODB_MIGRATION.md) for architecture details

## 🎯 Roadmap

- [ ] Real-time notifications
- [ ] Mobile app (React Native)
- [ ] Payment integration
- [ ] Advanced reporting
- [ ] Multi-language support
- [ ] API rate limiting
- [ ] Advanced caching with Redis (optional)
- [ ] Microservices architecture

---

**Built with ❤️ using Flask, React, and MongoDB** 