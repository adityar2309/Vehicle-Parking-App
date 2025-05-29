import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import SuccessMessage from '../components/SuccessMessage';

const AdminParkingLots = () => {
  const [parkingLots, setParkingLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingLot, setEditingLot] = useState(null);
  const [formData, setFormData] = useState({
    prime_location_name: '',
    address: '',
    pin_code: '',
    number_of_spots: '',
    price: ''
  });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [selectedLot, setSelectedLot] = useState(null);
  const [spots, setSpots] = useState([]);
  const [showSpotsModal, setShowSpotsModal] = useState(false);

  useEffect(() => {
    fetchParkingLots();
  }, []);

  const fetchParkingLots = async () => {
    try {
      setLoading(true);
      const response = await adminService.getParkingLots();
      setParkingLots(response.data.parking_lots || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load parking lots');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitLoading(true);
      setError('');
      
      const lotData = {
        ...formData,
        number_of_spots: parseInt(formData.number_of_spots),
        price: parseFloat(formData.price)
      };

      if (editingLot) {
        await adminService.updateParkingLot(editingLot.id, lotData);
        setSuccess('Parking lot updated successfully!');
      } else {
        await adminService.createParkingLot(lotData);
        setSuccess('Parking lot created successfully!');
      }
      
      await fetchParkingLots();
      handleCloseModal();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save parking lot');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDelete = async (lot) => {
    if (!window.confirm(`Are you sure you want to delete "${lot.prime_location_name}"?`)) {
      return;
    }

    try {
      await adminService.deleteParkingLot(lot.id);
      setSuccess('Parking lot deleted successfully!');
      await fetchParkingLots();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete parking lot');
    }
  };

  const handleEdit = (lot) => {
    setEditingLot(lot);
    setFormData({
      prime_location_name: lot.prime_location_name,
      address: lot.address,
      pin_code: lot.pin_code,
      number_of_spots: lot.number_of_spots.toString(),
      price: lot.price.toString()
    });
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingLot(null);
    setFormData({
      prime_location_name: '',
      address: '',
      pin_code: '',
      number_of_spots: '',
      price: ''
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingLot(null);
    setFormData({
      prime_location_name: '',
      address: '',
      pin_code: '',
      number_of_spots: '',
      price: ''
    });
  };

  const handleViewSpots = async (lot) => {
    try {
      setSelectedLot(lot);
      const response = await adminService.getParkingSpots(lot.id);
      setSpots(response.data.spots || []);
      setShowSpotsModal(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load parking spots');
    }
  };

  const getOccupancyRate = (lot) => {
    if (lot.number_of_spots === 0) return 0;
    const occupiedSpots = lot.number_of_spots - (lot.available_spots || 0);
    return Math.round((occupiedSpots / lot.number_of_spots) * 100);
  };

  const getOccupancyColor = (rate) => {
    if (rate < 50) return 'success';
    if (rate < 80) return 'warning';
    return 'danger';
  };

  if (loading) return <Loading />;

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-building me-2"></i>Parking Lots Management</h2>
            <div>
              <button className="btn btn-outline-primary me-2" onClick={fetchParkingLots}>
                <i className="bi bi-arrow-clockwise me-1"></i>Refresh
              </button>
              <button className="btn btn-primary" onClick={handleCreate}>
                <i className="bi bi-plus-lg me-1"></i>Add Parking Lot
              </button>
            </div>
          </div>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}
          {success && <SuccessMessage message={success} onClose={() => setSuccess('')} />}

          {/* Summary Cards */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-primary">{parkingLots.length}</h5>
                  <p className="card-text">Total Lots</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-info">
                    {parkingLots.reduce((sum, lot) => sum + lot.number_of_spots, 0)}
                  </h5>
                  <p className="card-text">Total Spots</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-success">
                    {parkingLots.reduce((sum, lot) => sum + (lot.available_spots || 0), 0)}
                  </h5>
                  <p className="card-text">Available</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-warning">
                    {parkingLots.reduce((sum, lot) => sum + (lot.number_of_spots - (lot.available_spots || 0)), 0)}
                  </h5>
                  <p className="card-text">Occupied</p>
                </div>
              </div>
            </div>
          </div>

          {/* Parking Lots Grid */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-grid me-2"></i>Parking Lots</h5>
            </div>
            <div className="card-body">
              {parkingLots.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-building display-1 text-muted"></i>
                  <p className="text-muted mt-2">No parking lots found</p>
                  <button className="btn btn-primary" onClick={handleCreate}>
                    <i className="bi bi-plus-lg me-1"></i>Create First Parking Lot
                  </button>
                </div>
              ) : (
                <div className="row">
                  {parkingLots.map(lot => {
                    const occupancyRate = getOccupancyRate(lot);
                    const occupancyColor = getOccupancyColor(occupancyRate);
                    
                    return (
                      <div key={lot.id} className="col-lg-6 col-xl-4 mb-4">
                        <div className="card h-100">
                          <div className="card-header d-flex justify-content-between align-items-center">
                            <h6 className="mb-0">{lot.prime_location_name}</h6>
                            <div className="dropdown">
                              <button className="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                      data-bs-toggle="dropdown">
                                <i className="bi bi-three-dots-vertical"></i>
                              </button>
                              <ul className="dropdown-menu">
                                <li>
                                  <button className="dropdown-item" onClick={() => handleViewSpots(lot)}>
                                    <i className="bi bi-grid-3x3 me-2"></i>View Spots
                                  </button>
                                </li>
                                <li>
                                  <button className="dropdown-item" onClick={() => handleEdit(lot)}>
                                    <i className="bi bi-pencil me-2"></i>Edit
                                  </button>
                                </li>
                                <li><hr className="dropdown-divider" /></li>
                                <li>
                                  <button className="dropdown-item text-danger" onClick={() => handleDelete(lot)}>
                                    <i className="bi bi-trash me-2"></i>Delete
                                  </button>
                                </li>
                              </ul>
                            </div>
                          </div>
                          <div className="card-body">
                            <p className="text-muted small mb-2">{lot.address}</p>
                            <p className="text-muted small mb-3">PIN: {lot.pin_code}</p>
                            
                            <div className="row text-center mb-3">
                              <div className="col-4">
                                <div className="fw-bold text-primary">{lot.number_of_spots}</div>
                                <small className="text-muted">Total</small>
                              </div>
                              <div className="col-4">
                                <div className="fw-bold text-success">{lot.available_spots || 0}</div>
                                <small className="text-muted">Available</small>
                              </div>
                              <div className="col-4">
                                <div className="fw-bold text-warning">{lot.number_of_spots - (lot.available_spots || 0)}</div>
                                <small className="text-muted">Occupied</small>
                              </div>
                            </div>

                            <div className="mb-3">
                              <div className="d-flex justify-content-between mb-1">
                                <small>Occupancy</small>
                                <small>{occupancyRate}%</small>
                              </div>
                              <div className="progress" style={{ height: '6px' }}>
                                <div className={`progress-bar bg-${occupancyColor}`} 
                                     style={{ width: `${occupancyRate}%` }}></div>
                              </div>
                            </div>

                            <div className="d-flex justify-content-between align-items-center">
                              <div className="fw-bold text-success">${lot.price}/hour</div>
                              <div>
                                <button className="btn btn-sm btn-outline-primary me-1" 
                                        onClick={() => handleViewSpots(lot)}>
                                  <i className="bi bi-eye"></i>
                                </button>
                                <button className="btn btn-sm btn-outline-secondary" 
                                        onClick={() => handleEdit(lot)}>
                                  <i className="bi bi-pencil"></i>
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot'}
                </h5>
                <button type="button" className="btn-close" onClick={handleCloseModal}></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Location Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.prime_location_name}
                      onChange={(e) => setFormData({...formData, prime_location_name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Address *</label>
                    <textarea
                      className="form-control"
                      rows="2"
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">PIN Code *</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.pin_code}
                      onChange={(e) => setFormData({...formData, pin_code: e.target.value})}
                      required
                    />
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Number of Spots *</label>
                      <input
                        type="number"
                        className="form-control"
                        min="1"
                        value={formData.number_of_spots}
                        onChange={(e) => setFormData({...formData, number_of_spots: e.target.value})}
                        required
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Price per Hour ($) *</label>
                      <input
                        type="number"
                        className="form-control"
                        min="0"
                        step="0.01"
                        value={formData.price}
                        onChange={(e) => setFormData({...formData, price: e.target.value})}
                        required
                      />
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={submitLoading}>
                    {submitLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        {editingLot ? 'Updating...' : 'Creating...'}
                      </>
                    ) : (
                      editingLot ? 'Update' : 'Create'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Spots Modal */}
      {showSpotsModal && selectedLot && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  Parking Spots - {selectedLot.prime_location_name}
                </h5>
                <button type="button" className="btn-close" onClick={() => setShowSpotsModal(false)}></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  {spots.map(spot => (
                    <div key={spot.id} className="col-md-3 col-sm-4 col-6 mb-3">
                      <div className={`card text-center ${spot.status === 'O' ? 'bg-danger text-white' : 'bg-success text-white'}`}>
                        <div className="card-body py-2">
                          <div className="fw-bold">{spot.spot_number}</div>
                          <small>{spot.status === 'O' ? 'Occupied' : 'Available'}</small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminParkingLots; 