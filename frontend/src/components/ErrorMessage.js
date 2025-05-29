import React from 'react';

const ErrorMessage = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="alert alert-danger alert-dismissible fade show" role="alert">
      <i className="bi bi-exclamation-triangle-fill me-2"></i>
      {message}
      {onDismiss && (
        <button
          type="button"
          className="btn-close"
          aria-label="Close"
          onClick={onDismiss}
        ></button>
      )}
    </div>
  );
};

export default ErrorMessage; 