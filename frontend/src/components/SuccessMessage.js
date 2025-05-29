import React from 'react';

const SuccessMessage = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="alert alert-success alert-dismissible fade show" role="alert">
      <i className="bi bi-check-circle-fill me-2"></i>
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

export default SuccessMessage; 