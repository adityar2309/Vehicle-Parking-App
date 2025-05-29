import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminService } from '../services/adminService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const ParkingSpotView = () => {
  const { lotId } = useParams();
  const navigate = useNavigate();
  const [lot, setLot] = useState(null);
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'available', 'occupied'

  useEffect(() => {
    if (lotId) {
      fetchParkingSpots();
    }
  }, [lotId]);

  const fetchParkingSpots = async () => {
    try {
      setLoading(true);
      const response = await adminService.getParkingSpots(lotId);
      setLot(response.data.lot);
      setSpots(response.data.spots || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load parking spots');
    } finally {
      setLoading(false);
    }
  };

  const getFilteredSpots = () => {
    if (filterStatus === 'all') return spots;
    return spots.filter(spot => 
      filterStatus === 'available' ? spot.status === 'A' : spot.status === 'O'
    );
  };

  const getOccupancyStats = () => {
    const totalSpots = spots.length;
    const occupiedSpots = spots.filter(spot => spot.status === 'O').length;
    const availableSpots = totalSpots - occupiedSpots;
    const occupancyRate = totalSpots > 0 ? Math.round((occupiedSpots / totalSpots) * 100) : 0;
    
    return { totalSpots, occupiedSpots, availableSpots, occupancyRate };
  };

  if (loading) return <Loading />;
  if (!lot) return <ErrorMessage message="Parking lot not found" />;

  const filteredSpots = getFilteredSpots();
  const { totalSpots, occupiedSpots, availableSpots, occupancyRate } = getOccupancyStats();

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          {/* Header */}
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <button className="btn btn-outline-secondary me-3" onClick={() => navigate(-1)}>
                <i className="bi bi-arrow-left me-1"></i>Back
              </button>
              <h2 className="d-inline">
                <i className="bi bi-grid-3x3 me-2"></i>
                {lot.prime_location_name} - Parking Spots
              </h2>
            </div>
            <button className="btn btn-outline-primary" onClick={fetchParkingSpots}>
              <i className="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
          </div>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}

          {/* Lot Information */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <h5>{lot.prime_location_name}</h5>
                  <p className="text-muted mb-1">{lot.address}</p>
                  <p className="text-muted">PIN Code: {lot.pin_code}</p>
                </div>
                <div className="col-md-4 text-end">
                  <div className="h4 text-success">${lot.price}/hour</div>
                  <div className="text-muted">Rate</div>
                </div>
              </div>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-primary">{totalSpots}</h5>
                  <p className="card-text">Total Spots</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-success">{availableSpots}</h5>
                  <p className="card-text">Available</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-danger">{occupiedSpots}</h5>
                  <p className="card-text">Occupied</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-warning">{occupancyRate}%</h5>
                  <p className="card-text">Occupancy Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Occupancy Progress Bar */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <h6>Occupancy Overview</h6>
                <span>{occupiedSpots}/{totalSpots} spots occupied</span>
              </div>
              <div className="progress" style={{ height: '20px' }}>
                <div className="progress-bar bg-danger" 
                     style={{ width: `${occupancyRate}%` }}>
                  {occupancyRate}%
                </div>
                <div className="progress-bar bg-success" 
                     style={{ width: `${100 - occupancyRate}%` }}>
                  {100 - occupancyRate}%
                </div>
              </div>
              <div className="d-flex justify-content-between mt-2">
                <small className="text-danger">
                  <i className="bi bi-square-fill me-1"></i>Occupied ({occupiedSpots})
                </small>
                <small className="text-success">
                  <i className="bi bi-square-fill me-1"></i>Available ({availableSpots})
                </small>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-md-4">
                  <label className="form-label">Filter by Status:</label>
                  <select 
                    className="form-select"
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <option value="all">All Spots ({totalSpots})</option>
                    <option value="available">Available Only ({availableSpots})</option>
                    <option value="occupied">Occupied Only ({occupiedSpots})</option>
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label">View Mode:</label>
                  <div className="btn-group w-100" role="group">
                    <button 
                      type="button" 
                      className={`btn btn-outline-primary ${viewMode === 'grid' ? 'active' : ''}`}
                      onClick={() => setViewMode('grid')}
                    >
                      <i className="bi bi-grid-3x3 me-1"></i>Grid
                    </button>
                    <button 
                      type="button" 
                      className={`btn btn-outline-primary ${viewMode === 'list' ? 'active' : ''}`}
                      onClick={() => setViewMode('list')}
                    >
                      <i className="bi bi-list me-1"></i>List
                    </button>
                  </div>
                </div>
                <div className="col-md-4 text-end">
                  <label className="form-label d-block">Legend:</label>
                  <span className="badge bg-success me-2">
                    <i className="bi bi-check-circle me-1"></i>Available
                  </span>
                  <span className="badge bg-danger">
                    <i className="bi bi-x-circle me-1"></i>Occupied
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Parking Spots Display */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-car-front me-2"></i>
                Parking Spots ({filteredSpots.length})
              </h5>
            </div>
            <div className="card-body">
              {filteredSpots.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-car-front-fill display-1 text-muted"></i>
                  <p className="text-muted mt-2">
                    No spots found matching the current filter
                  </p>
                </div>
              ) : viewMode === 'grid' ? (
                /* Grid View */
                <div className="row">
                  {filteredSpots.map(spot => (
                    <div key={spot.id} className="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6 mb-3">
                      <div className={`card text-center h-100 ${
                        spot.status === 'O' ? 'border-danger' : 'border-success'
                      }`}>
                        <div className={`card-body py-3 ${
                          spot.status === 'O' ? 'bg-danger text-white' : 'bg-success text-white'
                        }`}>
                          <div className="h5 mb-2">
                            <i className={`bi ${spot.status === 'O' ? 'bi-car-front-fill' : 'bi-car-front'}`}></i>
                          </div>
                          <div className="fw-bold">{spot.spot_number}</div>
                          <small>{spot.status === 'O' ? 'Occupied' : 'Available'}</small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                /* List View */
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-light">
                      <tr>
                        <th>Spot Number</th>
                        <th>Status</th>
                        <th>Last Updated</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSpots.map(spot => (
                        <tr key={spot.id}>
                          <td>
                            <div className="d-flex align-items-center">
                              <i className={`bi ${spot.status === 'O' ? 'bi-car-front-fill text-danger' : 'bi-car-front text-success'} me-2`}></i>
                              <span className="fw-bold">{spot.spot_number}</span>
                            </div>
                          </td>
                          <td>
                            {spot.status === 'O' ? (
                              <span className="badge bg-danger">
                                <i className="bi bi-x-circle me-1"></i>Occupied
                              </span>
                            ) : (
                              <span className="badge bg-success">
                                <i className="bi bi-check-circle me-1"></i>Available
                              </span>
                            )}
                          </td>
                          <td>
                            <small className="text-muted">
                              {new Date(spot.updated_at || spot.created_at).toLocaleString()}
                            </small>
                          </td>
                          <td>
                            <button className="btn btn-sm btn-outline-secondary" disabled>
                              <i className="bi bi-eye"></i>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0"><i className="bi bi-lightning me-2"></i>Quick Actions</h5>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <button className="btn btn-outline-primary w-100">
                        <i className="bi bi-download me-2"></i>Export Spot Data
                      </button>
                    </div>
                    <div className="col-md-4 mb-3">
                      <button className="btn btn-outline-info w-100">
                        <i className="bi bi-graph-up me-2"></i>View Analytics
                      </button>
                    </div>
                    <div className="col-md-4 mb-3">
                      <button className="btn btn-outline-warning w-100">
                        <i className="bi bi-gear me-2"></i>Manage Lot
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParkingSpotView; 