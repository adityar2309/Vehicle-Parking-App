# Vehicle Parking App - Testing Guide

## Pre-Testing Requirements

### 1. MongoDB Installation & Setup
Before testing, ensure MongoDB is installed and running:

#### Install MongoDB
```bash
# Windows - Download from https://www.mongodb.com/try/download/community
# Or use Chocolatey: choco install mongodb

# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community
```

#### Start MongoDB
```bash
# Windows
mongod

# Linux/macOS
sudo systemctl start mongod
# or
mongod --config /usr/local/etc/mongod.conf
```

#### Verify MongoDB is Running
```bash
# Connect to MongoDB
mongo
# or newer versions
mongosh

# In MongoDB shell, run:
show dbs
```

### 2. Environment Setup
1. Check if `.env` file exists in backend folder
2. If not, copy from `env_example.txt`:
   ```bash
   cd backend
   copy env_example.txt .env
   ```

## Testing Process

### Phase 1: Setup & Dependencies

#### Step 1: Install Dependencies
```bash
# Option 1: Use setup script
setup.bat

# Option 2: Manual installation
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..\frontend
npm install
```

#### Step 2: Verify Backend Dependencies
```bash
cd backend
venv\Scripts\activate
python -c "import pymongo, mongoengine, flask; print('All dependencies OK')"
```

### Phase 2: Backend Testing

#### Step 1: Database Initialization
```bash
cd backend
venv\Scripts\activate
python setup_backend.py
```

Expected output:
- MongoDB connection successful
- Collections created
- Admin user created (admin/admin123)
- Sample data inserted

#### Step 2: Start Backend Server
```bash
python app.py
```

Expected output:
```
MongoDB connected successfully
Cache service initialized successfully
Background services started successfully
* Running on http://127.0.0.1:5000
```

#### Step 3: Test Backend API Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Root Endpoint:**
```bash
curl http://localhost:5000/
```

**Test Login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Expected: JWT token returned

### Phase 3: Frontend Testing

#### Step 1: Start Frontend
```bash
cd frontend
npm start
```

Expected: Browser opens to http://localhost:3000

#### Step 2: Test Authentication Flow

**Admin Login:**
1. Navigate to login page
2. Enter credentials: admin/admin123
3. Verify redirect to admin dashboard

**Regular User Login:**
1. Create new user or use: testuser/password123
2. Test login flow
3. Verify redirect to user dashboard

### Phase 4: Feature Testing

#### Admin Features Test

**1. Dashboard:**
- [ ] View parking statistics
- [ ] See total users, lots, spots
- [ ] Check recent reservations
- [ ] Verify occupancy rates

**2. Parking Lot Management:**
- [ ] View all parking lots
- [ ] Create new parking lot
- [ ] Edit existing parking lot
- [ ] Delete empty parking lot
- [ ] View parking spots for each lot

**3. User Management:**
- [ ] View all users
- [ ] See user roles
- [ ] Check user activity

**4. Export Management:**
- [ ] View all export jobs
- [ ] Trigger cleanup of expired files

#### User Features Test

**1. Dashboard:**
- [ ] View personal statistics
- [ ] See current reservation
- [ ] Check recent bookings
- [ ] View available parking lots

**2. Booking Flow:**
- [ ] View available parking lots
- [ ] Book a parking spot
- [ ] Verify spot status changes
- [ ] Check booking confirmation

**3. Reservation Management:**
- [ ] View current reservation
- [ ] Release parking spot
- [ ] Calculate parking cost
- [ ] View reservation history

**4. CSV Export:**
- [ ] Request CSV export
- [ ] Check export status
- [ ] Download CSV file
- [ ] View export history

### Phase 5: MongoDB Data Verification

#### Step 1: Connect to MongoDB
```bash
mongo
# or
mongosh
```

#### Step 2: Check Collections
```javascript
use parking_app
show collections

// Should show:
// - users
// - parking_lots
// - parking_spots
// - reservations
// - export_jobs
// - user_activities
```

#### Step 3: Verify Data
```javascript
// Check users
db.users.find().pretty()

// Check parking lots
db.parking_lots.find().pretty()

// Check spots
db.parking_spots.find({status: "A"}).count()  // Available
db.parking_spots.find({status: "O"}).count()  // Occupied

// Check reservations
db.reservations.find().pretty()
```

### Phase 6: Background Jobs Testing

#### Test Job Execution
```bash
cd backend
venv\Scripts\activate
python -c "
from background_jobs import daily_reminder_job, monthly_report_job
print('Testing daily reminder...')
result = daily_reminder_job()
print(f'Result: {result}')
print('Testing monthly report...')
result = monthly_report_job()
print(f'Result: {result}')
"
```

### Phase 7: Cache Testing

#### Test Cache Operations
```bash
python -c "
from cache_service import CacheService, cache
# Test basic cache operations
cache.set('test_key', 'test_value', timeout=60)
print(f'Cache get: {cache.get(\"test_key\")}')
print('Cache test passed')
"
```

## Common Issues & Solutions

### MongoDB Issues

**Issue: MongoDB not running**
```
Solution: Start MongoDB service
mongod
```

**Issue: Connection refused**
```
Solution: Check MongoDB port and configuration
netstat -an | findstr 27017
```

### Backend Issues

**Issue: Module not found errors**
```
Solution: Activate virtual environment
cd backend
venv\Scripts\activate
```

**Issue: JWT Token errors**
```
Solution: Check JWT_SECRET_KEY in .env file
```

### Frontend Issues

**Issue: CORS errors**
```
Solution: Check CORS_ORIGINS in backend config.py
```

**Issue: API calls failing**
```
Solution: Verify backend is running on port 5000
```

## Test Data

### Default Admin Account
- Username: admin
- Password: admin123
- Role: admin

### Sample User Account
- Username: testuser
- Password: password123
- Role: user

### Sample Parking Lots
1. City Center Mall (50 spots, $5/hour)
2. Airport Terminal 1 (100 spots, $8/hour)
3. Business District Plaza (75 spots, $6.5/hour)

## Performance Testing

### Load Testing
```bash
# Test concurrent requests
for i in {1..10}; do
  curl http://localhost:5000/health &
done
wait
```

### Memory Usage
```bash
# Monitor Python process
tasklist | findstr python
```

## Security Testing

### Authentication Tests
- [ ] Test invalid credentials
- [ ] Test expired tokens
- [ ] Test role-based access
- [ ] Test unauthorized endpoints

### Input Validation
- [ ] Test SQL injection attempts
- [ ] Test XSS prevention
- [ ] Test input sanitization

## Conclusion

After completing all test phases:
1. Document any issues found
2. Verify all features work as expected
3. Check MongoDB data integrity
4. Confirm email notifications (if configured)
5. Test backup and recovery procedures

The app should be fully functional with:
- ✅ MongoDB database operations
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Parking management
- ✅ Synchronous background jobs
- ✅ Simple caching
- ✅ CSV export functionality 