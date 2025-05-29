import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import SuccessMessage from '../components/SuccessMessage';

const UserBooking = () => {
  const [parkingLots, setParkingLots] = useState([]);
  const [currentReservation, setCurrentReservation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [selectedLot, setSelectedLot] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [lotsResponse, reservationResponse] = await Promise.all([
        userService.getParkingLots(),
        userService.getCurrentReservation()
      ]);
      
      setParkingLots(lotsResponse.data.parking_lots || []);
      setCurrentReservation(reservationResponse.data.current_reservation);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load parking data');
    } finally {
      setLoading(false);
    }
  };

  const handleBookSpot = async (e) => {
    e.preventDefault();
    if (!selectedLot || !vehicleNumber.trim()) {
      setError('Please select a parking lot and enter vehicle number');
      return;
    }

    try {
      setBookingLoading(true);
      setError('');
      const response = await userService.bookSpot(selectedLot, vehicleNumber);
      setSuccess('Parking spot booked successfully!');
      setVehicleNumber('');
      setSelectedLot('');
      await fetchData(); // Refresh data
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to book parking spot');
    } finally {
      setBookingLoading(false);
    }
  };

  const handleReleaseSpot = async () => {
    try {
      setBookingLoading(true);
      setError('');
      const response = await userService.releaseSpot();
      setSuccess(`Spot released successfully! Cost: $${response.data.cost?.toFixed(2)}`);
      await fetchData(); // Refresh data
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to release parking spot');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-plus-circle me-2"></i>Book Parking Spot</h2>
            <button className="btn btn-outline-primary" onClick={fetchData}>
              <i className="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
          </div>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}
          {success && <SuccessMessage message={success} onClose={() => setSuccess('')} />}

          {/* Current Reservation */}
          {currentReservation && (
            <div className="card mb-4 border-warning">
              <div className="card-header bg-warning text-dark">
                <h5 className="mb-0"><i className="bi bi-car-front me-2"></i>Current Reservation</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6">
                    <p><strong>Parking Lot:</strong> {currentReservation.parking_lot_name}</p>
                    <p><strong>Spot Number:</strong> {currentReservation.spot_number}</p>
                    <p><strong>Vehicle:</strong> {currentReservation.vehicle_number}</p>
                  </div>
                  <div className="col-md-6">
                    <p><strong>Parked Since:</strong> {new Date(currentReservation.parking_timestamp).toLocaleString()}</p>
                    <p><strong>Address:</strong> {currentReservation.address}</p>
                    <button 
                      className="btn btn-danger"
                      onClick={handleReleaseSpot}
                      disabled={bookingLoading}
                    >
                      {bookingLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Releasing...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-car-front-fill me-1"></i>Release Spot
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Booking Form */}
          {!currentReservation && (
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0"><i className="bi bi-plus-circle me-2"></i>Book New Spot</h5>
              </div>
              <div className="card-body">
                <form onSubmit={handleBookSpot}>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Select Parking Lot *</label>
                      <select 
                        className="form-select"
                        value={selectedLot}
                        onChange={(e) => setSelectedLot(e.target.value)}
                        required
                      >
                        <option value="">Choose a parking lot...</option>
                        {parkingLots.map(lot => (
                          <option key={lot.id} value={lot.id}>
                            {lot.prime_location_name} - ${lot.price}/hr ({lot.available_spots} spots available)
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Vehicle Number *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={vehicleNumber}
                        onChange={(e) => setVehicleNumber(e.target.value)}
                        placeholder="Enter vehicle number"
                        required
                      />
                    </div>
                  </div>
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={bookingLoading || !selectedLot || !vehicleNumber.trim()}
                  >
                    {bookingLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Booking...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-plus-circle me-1"></i>Book Spot
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Available Parking Lots */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-building me-2"></i>Available Parking Lots</h5>
            </div>
            <div className="card-body">
              {parkingLots.length === 0 ? (
                <p className="text-muted">No parking lots available at the moment.</p>
              ) : (
                <div className="row">
                  {parkingLots.map(lot => (
                    <div key={lot.id} className="col-md-6 col-lg-4 mb-3">
                      <div className="card h-100">
                        <div className="card-body">
                          <h6 className="card-title">{lot.prime_location_name}</h6>
                          <p className="card-text text-muted small">{lot.address}</p>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <span className="badge bg-success">{lot.available_spots} available</span>
                              <span className="badge bg-secondary ms-1">{lot.number_of_spots} total</span>
                            </div>
                            <div className="text-end">
                              <div className="fw-bold text-primary">${lot.price}/hr</div>
                              <small className="text-muted">PIN: {lot.pin_code}</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserBooking; 