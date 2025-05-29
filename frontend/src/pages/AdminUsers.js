import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await adminService.getUsers();
      setUsers(response.data.users || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedUsers = () => {
    let filtered = users.filter(user => 
      user.username.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      if (sortField === 'created_at') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }
      
      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return filtered;
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field) => {
    if (sortField !== field) return 'bi-arrow-down-up';
    return sortDirection === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getActivityBadge = (user) => {
    const registeredDays = Math.floor((new Date() - new Date(user.created_at)) / (1000 * 60 * 60 * 24));
    if (registeredDays < 7) return <span className="badge bg-success">New</span>;
    if (registeredDays < 30) return <span className="badge bg-primary">Active</span>;
    return <span className="badge bg-secondary">Regular</span>;
  };

  if (loading) return <Loading />;

  const displayUsers = filteredAndSortedUsers();

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2><i className="bi bi-people me-2"></i>Users Management</h2>
            <button className="btn btn-outline-primary" onClick={fetchUsers}>
              <i className="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
          </div>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}

          {/* Summary Cards */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-primary">{users.length}</h5>
                  <p className="card-text">Total Users</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-success">
                    {users.filter(u => {
                      const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                      return days < 7;
                    }).length}
                  </h5>
                  <p className="card-text">New (7 days)</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-info">
                    {users.filter(u => {
                      const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                      return days >= 7 && days < 30;
                    }).length}
                  </h5>
                  <p className="card-text">Active (30 days)</p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title text-warning">
                    {users.filter(u => {
                      const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                      return days >= 30;
                    }).length}
                  </h5>
                  <p className="card-text">Regular (30+ days)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Search and Filter Controls */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-md-6">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search by username..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-md-6 text-end">
                  <small className="text-muted">
                    Showing {displayUsers.length} of {users.length} users
                  </small>
                </div>
              </div>
            </div>
          </div>

          {/* Users Table */}
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0"><i className="bi bi-table me-2"></i>Users List</h5>
            </div>
            <div className="card-body">
              {displayUsers.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-people display-1 text-muted"></i>
                  <p className="text-muted mt-2">
                    {searchTerm ? 'No users found matching your search' : 'No users found'}
                  </p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead className="table-light">
                      <tr>
                        <th>
                          <button 
                            className="btn btn-link text-decoration-none p-0 text-dark fw-bold"
                            onClick={() => handleSort('username')}
                          >
                            Username <i className={`bi ${getSortIcon('username')}`}></i>
                          </button>
                        </th>
                        <th>Status</th>
                        <th>
                          <button 
                            className="btn btn-link text-decoration-none p-0 text-dark fw-bold"
                            onClick={() => handleSort('created_at')}
                          >
                            Registered <i className={`bi ${getSortIcon('created_at')}`}></i>
                          </button>
                        </th>
                        <th>Total Reservations</th>
                        <th>Total Spent</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displayUsers.map(user => {
                        const registeredDays = Math.floor((new Date() - new Date(user.created_at)) / (1000 * 60 * 60 * 24));
                        
                        return (
                          <tr key={user.id}>
                            <td>
                              <div className="d-flex align-items-center">
                                <div className="me-3">
                                  <div className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" 
                                       style={{ width: '40px', height: '40px' }}>
                                    {user.username.charAt(0).toUpperCase()}
                                  </div>
                                </div>
                                <div>
                                  <div className="fw-bold">{user.username}</div>
                                  <small className="text-muted">ID: {user.id}</small>
                                </div>
                              </div>
                            </td>
                            <td>
                              {getActivityBadge(user)}
                            </td>
                            <td>
                              <div>
                                <div>{formatDate(user.created_at)}</div>
                                <small className="text-muted">
                                  {registeredDays === 0 ? 'Today' : 
                                   registeredDays === 1 ? '1 day ago' : 
                                   `${registeredDays} days ago`}
                                </small>
                              </div>
                            </td>
                            <td>
                              <span className="badge bg-info">
                                {user.total_reservations || 0}
                              </span>
                            </td>
                            <td>
                              <span className="fw-bold text-success">
                                ${(user.total_spent || 0).toFixed(2)}
                              </span>
                            </td>
                            <td>
                              <div className="dropdown">
                                <button className="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                        data-bs-toggle="dropdown">
                                  <i className="bi bi-three-dots"></i>
                                </button>
                                <ul className="dropdown-menu">
                                  <li>
                                    <button className="dropdown-item">
                                      <i className="bi bi-eye me-2"></i>View Details
                                    </button>
                                  </li>
                                  <li>
                                    <button className="dropdown-item">
                                      <i className="bi bi-list-check me-2"></i>View Reservations
                                    </button>
                                  </li>
                                  <li><hr className="dropdown-divider" /></li>
                                  <li>
                                    <button className="dropdown-item text-warning">
                                      <i className="bi bi-person-x me-2"></i>Suspend User
                                    </button>
                                  </li>
                                </ul>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* User Registration Chart Section */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0"><i className="bi bi-graph-up me-2"></i>User Registration Trends</h5>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-6">
                      <h6>Registration by Period</h6>
                      <div className="mb-2">
                        <div className="d-flex justify-content-between">
                          <span>Last 7 days</span>
                          <span className="badge bg-success">
                            {users.filter(u => {
                              const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                              return days < 7;
                            }).length}
                          </span>
                        </div>
                        <div className="progress mb-2" style={{ height: '6px' }}>
                          <div className="progress-bar bg-success" 
                               style={{ width: `${(users.filter(u => {
                                 const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                                 return days < 7;
                               }).length / users.length) * 100}%` }}></div>
                        </div>
                      </div>
                      
                      <div className="mb-2">
                        <div className="d-flex justify-content-between">
                          <span>Last 30 days</span>
                          <span className="badge bg-primary">
                            {users.filter(u => {
                              const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                              return days < 30;
                            }).length}
                          </span>
                        </div>
                        <div className="progress mb-2" style={{ height: '6px' }}>
                          <div className="progress-bar bg-primary" 
                               style={{ width: `${(users.filter(u => {
                                 const days = Math.floor((new Date() - new Date(u.created_at)) / (1000 * 60 * 60 * 24));
                                 return days < 30;
                               }).length / users.length) * 100}%` }}></div>
                        </div>
                      </div>
                      
                      <div className="mb-2">
                        <div className="d-flex justify-content-between">
                          <span>All time</span>
                          <span className="badge bg-secondary">{users.length}</span>
                        </div>
                        <div className="progress" style={{ height: '6px' }}>
                          <div className="progress-bar bg-secondary" style={{ width: '100%' }}></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="col-md-6">
                      <h6>User Activity Stats</h6>
                      <div className="row text-center">
                        <div className="col-4">
                          <div className="p-3">
                            <div className="h4 text-success mb-1">
                              {users.reduce((sum, u) => sum + (u.total_reservations || 0), 0)}
                            </div>
                            <small className="text-muted">Total Bookings</small>
                          </div>
                        </div>
                        <div className="col-4">
                          <div className="p-3">
                            <div className="h4 text-info mb-1">
                              ${users.reduce((sum, u) => sum + (u.total_spent || 0), 0).toFixed(0)}
                            </div>
                            <small className="text-muted">Total Revenue</small>
                          </div>
                        </div>
                        <div className="col-4">
                          <div className="p-3">
                            <div className="h4 text-warning mb-1">
                              {users.length > 0 ? (users.reduce((sum, u) => sum + (u.total_reservations || 0), 0) / users.length).toFixed(1) : 0}
                            </div>
                            <small className="text-muted">Avg per User</small>
                          </div>
                        </div>
                      </div>
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

export default AdminUsers; 