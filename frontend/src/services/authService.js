import api from './api';

class AuthService {
  async login(username, password) {
    try {
      const response = await api.post('/auth/login', {
        username,
        password,
      });

      const { access_token, user } = response.data;
      
      // Store token and user info
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      };
    }
  }

  async register(username, password) {
    try {
      const response = await api.post('/auth/register', {
        username,
        password,
      });

      return { success: true, user: response.data.user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed',
      };
    }
  }

  async verifyToken() {
    try {
      const response = await api.get('/auth/verify');
      return { success: true, user: response.data.user };
    } catch (error) {
      return { success: false };
    }
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  isAdmin() {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }

  isUser() {
    const user = this.getCurrentUser();
    return user?.role === 'user';
  }
}

export default new AuthService(); 