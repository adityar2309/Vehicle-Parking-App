import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import authService from '../services/authService';
import ErrorMessage from '../components/ErrorMessage';
import Loading from '../components/Loading';
import { validateUsername, validatePassword } from '../utils/helpers';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    const usernameError = validateUsername(formData.username);
    if (usernameError) {
      newErrors.username = usernameError;
    }

    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      newErrors.password = passwordError;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await authService.login(formData.username, formData.password);
      
      if (result.success) {
        onLogin(result.user);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading message="Signing you in..." />;
  }

  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body p-5">
              <div className="text-center mb-4">
                <i className="bi bi-car-front-fill text-primary" style={{ fontSize: '3rem' }}></i>
                <h3 className="mt-2">Vehicle Parking App</h3>
                <p className="text-muted">Sign in to your account</p>
              </div>

              <ErrorMessage message={error} onDismiss={() => setError('')} />

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="username" className="form-label">Username</label>
                  <input
                    type="text"
                    className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    required
                  />
                  {errors.username && <div className="invalid-feedback">{errors.username}</div>}
                </div>

                <div className="mb-3">
                  <label htmlFor="password" className="form-label">Password</label>
                  <input
                    type="password"
                    className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    required
                  />
                  {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={loading}
                >
                  <i className="bi bi-box-arrow-in-right me-2"></i>
                  Sign In
                </button>
              </form>

              <div className="text-center mt-4">
                <p className="mb-2">Don't have an account?</p>
                <Link to="/register" className="btn btn-outline-secondary">
                  <i className="bi bi-person-plus me-2"></i>
                  Create Account
                </Link>
              </div>

              <div className="mt-4 p-3 bg-light rounded">
                <h6 className="text-muted mb-2">Demo Credentials:</h6>
                <small className="text-muted">
                  <strong>Admin:</strong> admin / admin123<br />
                  <strong>User:</strong> Register a new account
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 