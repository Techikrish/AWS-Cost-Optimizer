import React from 'react';

export default function Header({ loggedIn, user, onLogout }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <span className="logo-icon">💰</span>
          <h1>AWS Cost Optimizer</h1>
        </div>
        {loggedIn && (
          <div className="user-info">
            <span className="user-name">👤 {user}</span>
            <button onClick={onLogout} className="btn-logout">Logout</button>
          </div>
        )}
      </div>
    </header>
  );
}
