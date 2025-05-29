import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../services/adminService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import { formatNumber, formatCurrency } from '../utils/helpers';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const result = await adminService.getDashboardData();
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

  const { summary, lot_stats, recent_reservations } = dashboardData || {};

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-speedometer2 me-2"></i>Admin Dashboard</h2>
            <div className="btn-group">
              <Link to="/admin/parking-lots" className="btn btn-primary">
                <i className="bi bi-building me-1"></i>
                Manage Parking Lots
              </Link>
              <Link to="/admin/users" className="btn btn-outline-primary">
                <i className="bi bi-people me-1"></i>
                View Users
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-building text-primary" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{formatNumber(summary?.total_lots || 0)}</h3>
              <p className="text-muted mb-0">Total Parking Lots</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-car-front text-info" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{formatNumber(summary?.total_spots || 0)}</h3>
              <p className="text-muted mb-0">Total Parking Spots</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-check-circle text-success" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{formatNumber(summary?.available_spots || 0)}</h3>
              <p className="text-muted mb-0">Available Spots</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stats-card">
            <div className="card-body text-center">
              <i className="bi bi-x-circle text-danger" style={{ fontSize: '2rem' }}></i>
              <h3 className="mt-2">{formatNumber(summary?.occupied_spots || 0)}</h3>
              <p className="text-muted mb-0">Occupied Spots</p>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Parking Lot Statistics */}
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-bar-chart me-2"></i>Parking Lot Statistics</h5>
            </div>
            <div className="card-body">
              {lot_stats && lot_stats.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Parking Lot</th>
                        <th>Total Spots</th>
                        <th>Occupied</th>
                        <th>Available</th>
                        <th>Occupancy Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lot_stats.map((lot, index) => (
                        <tr key={index}>
                          <td>{lot.lot_name}</td>
                          <td>{lot.total_spots}</td>
                          <td>
                            <span className="badge bg-danger">{lot.occupied_spots}</span>
                          </td>
                          <td>
                            <span className="badge bg-success">{lot.available_spots}</span>
                          </td>
                          <td>
                            <div className="progress" style={{ height: '20px' }}>
                              <div
                                className="progress-bar"
                                role="progressbar"
                                style={{ width: `${lot.occupancy_rate}%` }}
                                aria-valuenow={lot.occupancy_rate}
                                aria-valuemin="0"
                                aria-valuemax="100"
                              >
                                {lot.occupancy_rate}%
                              </div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted">No parking lots available.</p>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-clock-history me-2"></i>Recent Reservations</h5>
            </div>
            <div className="card-body">
              {recent_reservations && recent_reservations.length > 0 ? (
                <div className="list-group list-group-flush">
                  {recent_reservations.slice(0, 5).map((reservation) => (
                    <div key={reservation.id} className="list-group-item border-0 px-0">
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 className="mb-1">{reservation.lot_name}</h6>
                          <p className="mb-1 small text-muted">
                            Spot: {reservation.spot_number}
                          </p>
                          <small className="text-muted">
                            Vehicle: {reservation.vehicle_number}
                          </small>
                        </div>
                        <span className={`badge ${reservation.status === 'Active' ? 'bg-success' : 'bg-secondary'}`}>
                          {reservation.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No recent reservations.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 