import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = ({ user, onLogout }) => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          <i className="bi bi-car-front-fill me-2"></i>
          Vehicle Parking App
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {user?.role === 'admin' ? (
              <>
                <li className="nav-item">
                  <Link className={isActive('/admin')} to="/admin">
                    <i className="bi bi-speedometer2 me-1"></i>
                    Dashboard
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className={isActive('/admin/parking-lots')} to="/admin/parking-lots">
                    <i className="bi bi-building me-1"></i>
                    Parking Lots
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className={isActive('/admin/users')} to="/admin/users">
                    <i className="bi bi-people me-1"></i>
                    Users
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link className={isActive('/dashboard')} to="/dashboard">
                    <i className="bi bi-speedometer2 me-1"></i>
                    Dashboard
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className={isActive('/booking')} to="/booking">
                    <i className="bi bi-plus-circle me-1"></i>
                    Book Parking
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className={isActive('/reservations')} to="/reservations">
                    <i className="bi bi-list-check me-1"></i>
                    My Reservations
                  </Link>
                </li>
              </>
            )}
          </ul>

          <ul className="navbar-nav">
            <li className="nav-item dropdown">
              <a
                className="nav-link dropdown-toggle"
                href="#"
                id="navbarDropdown"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="bi bi-person-circle me-1"></i>
                {user?.username}
                <span className={`badge ms-2 ${user?.role === 'admin' ? 'bg-danger' : 'bg-success'}`}>
                  {user?.role?.toUpperCase()}
                </span>
              </a>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <a className="dropdown-item" href="#" onClick={onLogout}>
                    <i className="bi bi-box-arrow-right me-1"></i>
                    Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 