import api from './api';

class UserService {
  // Parking Lot Operations
  async getParkingLots() {
    return await api.get('/user/parking-lots');
  }

  // Booking Operations
  async bookSpot(lotId, vehicleNumber) {
    return await api.post('/user/book-spot', {
      lot_id: lotId,
      vehicle_number: vehicleNumber,
    });
  }

  async releaseSpot() {
    return await api.post('/user/release-spot');
  }

  // Reservation History
  async getReservations(page = 1, perPage = 10) {
    return await api.get(`/user/reservations?page=${page}&per_page=${perPage}`);
  }

  async getCurrentReservation() {
    return await api.get('/user/current-reservation');
  }

  // Dashboard Data
  async getDashboardData() {
    return await api.get('/user/dashboard');
  }
}

export const userService = new UserService(); 