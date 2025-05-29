import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import authService from './services/authService';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import UserDashboard from './pages/UserDashboard';
import AdminParkingLots from './pages/AdminParkingLots';
import AdminUsers from './pages/AdminUsers';
import UserBooking from './pages/UserBooking';
import UserReservations from './pages/UserReservations';
import ParkingSpotView from './pages/ParkingSpotView';

// Components
import Navbar from './components/Navbar';
import Loading from './components/Loading';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      if (authService.isAuthenticated()) {
        const result = await authService.verifyToken();
        if (result.success) {
          setUser(result.user);
        } else {
          authService.logout();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <Router>
      <div className="App">
        {user && <Navbar user={user} onLogout={handleLogout} />}
        <div className={user ? 'container-fluid mt-4' : ''}>
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                !user ? (
                  <Login onLogin={handleLogin} />
                ) : (
                  <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />
                )
              }
            />
            <Route
              path="/register"
              element={
                !user ? (
                  <Register />
                ) : (
                  <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />
                )
              }
            />

            {/* Admin Routes */}
            {user?.role === 'admin' && (
              <>
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/parking-lots" element={<AdminParkingLots />} />
                <Route path="/admin/parking-lots/:id/spots" element={<ParkingSpotView />} />
                <Route path="/admin/users" element={<AdminUsers />} />
              </>
            )}

            {/* User Routes */}
            {user?.role === 'user' && (
              <>
                <Route path="/dashboard" element={<UserDashboard />} />
                <Route path="/booking" element={<UserBooking />} />
                <Route path="/reservations" element={<UserReservations />} />
              </>
            )}

            {/* Default Redirects */}
            <Route
              path="/"
              element={
                user ? (
                  <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            {/* Catch all route */}
            <Route
              path="*"
              element={
                <Navigate to={user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/login'} replace />
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App; 