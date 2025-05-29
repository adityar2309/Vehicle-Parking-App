import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { userService } from '../services/userService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import { formatCurrency, formatDate, getStatusBadgeClass } from '../utils/helpers';

const UserDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const result = await userService.getDashboardData();
      setDashboardData(result.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="container">
        <ErrorMessage message={error} />
      </div>
    );
  }

  const { summary, current_reservation, recent_reservations } = dashboardData || {};

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-speedometer2 me-2"></i>My Dashboard</h2>
            <div className="btn-group">
              <Link to="/booking" className="btn btn-primary">
                <i className="bi bi-plus-circle me-1"></i>
                Book Parking
              </Link>
              <Link to="/reservations" className="btn btn-outline-primary">
                <i className="bi bi-list-check me-1"></i>
                View All Reservations
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Current Reservation Alert */}
      {current_reservation && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="alert alert-info">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="alert-heading mb-1">
                    <i className="bi bi-car-front me-2"></i>
                    Current Parking Session
                  </h5>
                  <p className="mb-1">
                    <strong>Location:</strong> {current_reservation.lot_name} - Spot {current_reservation.spot_number}
                  </p>
                  <p className="mb-0">
                    <strong>Vehicle:</strong> {current_reservation.vehicle_number} | 
                    <strong> Started:</strong> {formatDate(current_reservation.parking_timestamp)}
                  </p>
                </div>
                <Link to="/booking" className="btn btn-outline-info">
                  <i className="bi bi-box-arrow-right me-1"></i>
                  Release Spot
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-calendar-check text-primary" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{summary?.total_reservations || 0}</h3>
              <p className="text-muted mb-0">Total Reservations</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-check-circle text-success" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{summary?.completed_reservations || 0}</h3>
              <p className="text-muted mb-0">Completed</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-hourglass-split text-warning" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{summary?.active_reservations || 0}</h3>
              <p className="text-muted mb-0">Active</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-currency-dollar text-info" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{formatCurrency(summary?.total_spent || 0)}</h3>
              <p className="text-muted mb-0">Total Spent</p>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Recent Reservations */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-clock-history me-2"></i>Recent Reservations</h5>
            </div>
            <div className="card-body">
              {recent_reservations && recent_reservations.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Parking Lot</th>
                        <th>Spot</th>
                        <th>Vehicle</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Cost</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recent_reservations.map((reservation) => (
                        <tr key={reservation.id}>
                          <td>{reservation.lot_name}</td>
                          <td>{reservation.spot_number}</td>
                          <td>{reservation.vehicle_number}</td>
                          <td>{formatDate(reservation.parking_timestamp)}</td>
                          <td>{reservation.leaving_timestamp ? formatDate(reservation.leaving_timestamp) : '-'}</td>
                          <td>{reservation.parking_cost ? formatCurrency(reservation.parking_cost) : '-'}</td>
                          <td>
                            <span className={getStatusBadgeClass(reservation.status)}>
                              {reservation.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="bi bi-inbox text-muted" style={{ fontSize: '3rem' }}></i>
                  <h5 className="mt-3 text-muted">No reservations yet</h5>
                  <p className="text-muted">Start by booking your first parking spot!</p>
                  <Link to="/booking" className="btn btn-primary">
                    <i className="bi bi-plus-circle me-1"></i>
                    Book Now
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard; 