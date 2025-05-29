// Date formatting utilities
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatTime = (dateString) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '$0.00';
  return `$${parseFloat(amount).toFixed(2)}`;
};

// Duration calculation
export const calculateDuration = (startTime, endTime) => {
  if (!startTime) return 'N/A';
  
  const start = new Date(startTime);
  const end = endTime ? new Date(endTime) : new Date();
  
  const diffMs = end - start;
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (diffHours > 0) {
    return `${diffHours}h ${diffMinutes}m`;
  }
  return `${diffMinutes}m`;
};

// Form validation utilities
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUsername = (username) => {
  if (!username || username.length < 3) {
    return 'Username must be at least 3 characters long';
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return 'Username can only contain letters, numbers, and underscores';
  }
  return null;
};

export const validatePassword = (password) => {
  if (!password || password.length < 6) {
    return 'Password must be at least 6 characters long';
  }
  return null;
};

export const validateVehicleNumber = (vehicleNumber) => {
  if (!vehicleNumber || vehicleNumber.trim().length === 0) {
    return 'Vehicle number is required';
  }
  if (vehicleNumber.trim().length < 3) {
    return 'Vehicle number must be at least 3 characters long';
  }
  return null;
};

// Status formatting
export const getStatusBadgeClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'active':
      return 'badge bg-success';
    case 'completed':
      return 'badge bg-secondary';
    case 'available':
      return 'badge bg-success';
    case 'occupied':
      return 'badge bg-danger';
    default:
      return 'badge bg-secondary';
  }
};

// Number formatting
export const formatNumber = (number) => {
  if (number === null || number === undefined) return '0';
  return number.toLocaleString();
};

export const formatPercentage = (value, total) => {
  if (!total || total === 0) return '0%';
  return `${Math.round((value / total) * 100)}%`;
};

// Local storage utilities
export const getFromStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error reading from localStorage:`, error);
    return defaultValue;
  }
};

export const setToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error writing to localStorage:`, error);
  }
};

export const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Error removing from localStorage:`, error);
  }
};

// Debounce utility for search inputs
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}; 