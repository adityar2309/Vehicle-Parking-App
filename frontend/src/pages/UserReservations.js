import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const UserReservations = () => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    pages: 0,
    per_page: 10,
    total: 0,
    has_next: false,
    has_prev: false
  });

  useEffect(() => {
    fetchReservations();
  }, [pagination.page]);

  const fetchReservations = async () => {
    try {
      setLoading(true);
      const response = await userService.getReservations(pagination.page, pagination.per_page);
      setReservations(response.data.reservations || []);
      setPagination(response.data.pagination);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (start, end) => {
    if (!end) return 'Ongoing';
    const startTime = new Date(start);
    const endTime = new Date(end);
    const durationMs = endTime - startTime;
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const getStatusBadge = (reservation) => {
    if (!reservation.leaving_timestamp) {
      return <span className="badge bg-warning">Active</span>;
    }
    return <span className="badge bg-success">Completed</span>;
  };

  if (loading) return <Loading />;

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-list-check me-2"></i>My Reservations</h2>
            <button className="btn btn-outline-primary" onClick={fetchReservations}>
              <i className="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
          </div>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}

          {/* Reservations Summary */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-primary">{pagination.total}</h5>
                  <p className="card-text">Total Reservations</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-warning">
                    {reservations.filter(r => !r.leaving_timestamp).length}
                  </h5>
                  <p className="card-text">Active</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-success">
                    {reservations.filter(r => r.leaving_timestamp).length}
                  </h5>
                  <p className="card-text">Completed</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-info">
                    ${reservations.reduce((sum, r) => sum + (r.parking_cost || 0), 0).toFixed(2)}
                  </h5>
                  <p className="card-text">Total Spent</p>
                </div>
              </div>
            </div>
          </div>

          {/* Reservations Table */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-table me-2"></i>Reservation History</h5>
            </div>
            <div className="card-body">
              {reservations.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-inbox display-1 text-muted"></i>
                  <p className="text-muted mt-2">No reservations found</p>
                </div>
              ) : (
                <>
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead className="table-light">
                        <tr>
                          <th>Status</th>
                          <th>Parking Lot</th>
                          <th>Spot</th>
                          <th>Vehicle</th>
                          <th>Check-in</th>
                          <th>Check-out</th>
                          <th>Duration</th>
                          <th>Cost</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reservations.map(reservation => (
                          <tr key={reservation.id}>
                            <td>{getStatusBadge(reservation)}</td>
                            <td>
                              <div>
                                <div className="fw-bold">{reservation.parking_lot_name}</div>
                                <small className="text-muted">{reservation.address}</small>
                              </div>
                            </td>
                            <td>
                              <span className="badge bg-secondary">{reservation.spot_number}</span>
                            </td>
                            <td>
                              <span className="font-monospace">{reservation.vehicle_number}</span>
                            </td>
                            <td>
                              <small>{formatDate(reservation.parking_timestamp)}</small>
                            </td>
                            <td>
                              {reservation.leaving_timestamp ? (
                                <small>{formatDate(reservation.leaving_timestamp)}</small>
                              ) : (
                                <span className="text-warning">
                                  <i className="bi bi-clock me-1"></i>Ongoing
                                </span>
                              )}
                            </td>
                            <td>
                              <span className="badge bg-info">
                                {formatDuration(reservation.parking_timestamp, reservation.leaving_timestamp)}
                              </span>
                            </td>
                            <td>
                              {reservation.parking_cost ? (
                                <span className="fw-bold text-success">
                                  ${reservation.parking_cost.toFixed(2)}
                                </span>
                              ) : (
                                <span className="text-muted">Calculating...</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  {pagination.pages > 1 && (
                    <nav className="mt-3">
                      <ul className="pagination justify-content-center">
                        <li className={`page-item ${!pagination.has_prev ? 'disabled' : ''}`}>
                          <button 
                            className="page-link"
                            onClick={() => handlePageChange(pagination.page - 1)}
                            disabled={!pagination.has_prev}
                          >
                            <i className="bi bi-chevron-left"></i>
                          </button>
                        </li>
                        
                        {[...Array(pagination.pages)].map((_, index) => {
                          const pageNum = index + 1;
                          const isActive = pageNum === pagination.page;
                          const showPage = pageNum === 1 || 
                                         pageNum === pagination.pages || 
                                         Math.abs(pageNum - pagination.page) <= 2;
                          
                          if (!showPage) {
                            if (pageNum === pagination.page - 3 || pageNum === pagination.page + 3) {
                              return <li key={pageNum} className="page-item disabled">
                                <span className="page-link">...</span>
                              </li>;
                            }
                            return null;
                          }
                          
                          return (
                            <li key={pageNum} className={`page-item ${isActive ? 'active' : ''}`}>
                              <button 
                                className="page-link"
                                onClick={() => handlePageChange(pageNum)}
                              >
                                {pageNum}
                              </button>
                            </li>
                          );
                        })}
                        
                        <li className={`page-item ${!pagination.has_next ? 'disabled' : ''}`}>
                          <button 
                            className="page-link"
                            onClick={() => handlePageChange(pagination.page + 1)}
                            disabled={!pagination.has_next}
                          >
                            <i className="bi bi-chevron-right"></i>
                          </button>
                        </li>
                      </ul>
                      
                      <div className="text-center text-muted">
                        Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
                        {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
                        {pagination.total} reservations
                      </div>
                    </nav>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserReservations; 