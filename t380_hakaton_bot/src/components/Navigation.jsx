import React from 'react';
import './Navigation.css';

const Navigation = ({ currentPage, setCurrentPage }) => {
  return (
    <nav className="navigation">
      <button
        className={`nav-button ${currentPage === 'main' ? 'active' : ''}`}
        onClick={() => setCurrentPage('main')}
      >
        <span className="nav-icon">🏠</span>
        <span className="nav-label">Главная</span>
      </button>
      <button
        className={`nav-button ${currentPage === 'calendar' ? 'active' : ''}`}
        onClick={() => setCurrentPage('calendar')}
      >
        <span className="nav-icon">📅</span>
        <span className="nav-label">Календарь</span>
      </button>
      <button
        className={`nav-button ${currentPage === 'settings' ? 'active' : ''}`}
        onClick={() => setCurrentPage('settings')}
      >
        <span className="nav-icon">⚙️</span>
        <span className="nav-label">Настройки</span>
      </button>
    </nav>
  );
};

export default Navigation;

