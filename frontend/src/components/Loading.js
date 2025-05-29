import React from 'react';

const Loading = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-spinner">
      <div className="text-center">
        <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
          <span className="visually-hidden">Loading...</span>
        </div>
        <div className="mt-3">
          <h5 className="text-muted">{message}</h5>
        </div>
      </div>
    </div>
  );
};

export default Loading; 