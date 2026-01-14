import React from 'react';

export default function TechniqueCard({ technique, onAnalyze, loading }) {
  return (
    <div className="technique-card">
      <div className="card-header">
        <span className="card-icon">{technique.icon}</span>
        <h3>{technique.name}</h3>
      </div>
      <p className="card-description">{technique.description}</p>
      <button
        onClick={() => onAnalyze(technique)}
        className="btn btn-secondary"
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
  );
}
