import api from './api';

class AdminService {
  // Parking Lot Management
  async getParkingLots() {
    return await api.get('/admin/parking-lots');
  }

  async createParkingLot(lotData) {
    return await api.post('/admin/parking-lots', lotData);
  }

  async updateParkingLot(lotId, lotData) {
    return await api.put(`/admin/parking-lots/${lotId}`, lotData);
  }

  async deleteParkingLot(lotId) {
    return await api.delete(`/admin/parking-lots/${lotId}`);
  }

  async getParkingSpots(lotId) {
    return await api.get(`/admin/parking-lots/${lotId}/spots`);
  }

  // User Management
  async getUsers() {
    return await api.get('/admin/users');
  }

  // Dashboard Data
  async getDashboardData() {
    return await api.get('/admin/dashboard');
  }
}

export const adminService = new AdminService(); 