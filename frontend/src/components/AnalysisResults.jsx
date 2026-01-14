import React, { useState } from 'react';
import ResourceList from './ResourceList';

export default function AnalysisResults({ results, onOptimize, onBack, dryRun, setDryRun, loading }) {
  const [selectedIds, setSelectedIds] = useState([]);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationInput, setConfirmationInput] = useState('');
  const [confirmationError, setConfirmationError] = useState('');

  const handleSelectAll = () => {
    if (selectedIds.length === results.findings.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(results.findings.map(f => f.resource_id));
    }
  };

  const handleToggleResource = (resourceId) => {
    setSelectedIds(prev =>
      prev.includes(resourceId)
        ? prev.filter(id => id !== resourceId)
        : [...prev, resourceId]
    );
  };

  const handleOptimize = () => {
    if (selectedIds.length === 0) {
      alert('Please select resources to optimize');
      return;
    }
    // Show confirmation dialog
    setShowConfirmation(true);
    setConfirmationInput('');
    setConfirmationError('');
  };

  const handleConfirmOptimization = () => {
    const serviceName = results.technique.name.toLowerCase();
    const inputLower = confirmationInput.toLowerCase().trim();
    
    // Check if input matches the service name (flexible matching)
    const isValid = 
      inputLower === serviceName ||
      inputLower === results.technique.id ||
      inputLower.includes(serviceName.split(' ')[0]);
    
    if (!isValid) {
      setConfirmationError(`Please type "${results.technique.name}" to confirm`);
      return;
    }
    
    setShowConfirmation(false);
    setConfirmationInput('');
    setConfirmationError('');
    onOptimize(selectedIds);
  };

  const exportAsJSON = () => {
    const data = {
      technique: results.technique.name,
      findings: results.findings,
      total_monthly_savings: results.total_monthly_savings,
      exported_at: new Date().toISOString()
    };
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(data, null, 2)));
    element.setAttribute('download', `cost-optimizer-${results.technique.id}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const exportAsCSV = () => {
    let csv = 'Resource ID,Type,Details,Estimated Monthly Savings\n';
    results.findings.forEach(f => {
      const details = JSON.stringify(f.details).replace(/"/g, '""');
      csv += `"${f.resource_id}","${f.resource_type}","${details}","${f.estimated_savings}"\n`;
    });
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv));
    element.setAttribute('download', `cost-optimizer-${results.technique.id}.csv`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="analysis-results">
      {showConfirmation && (
        <div className="modal-overlay">
          <div className="confirmation-modal">
            <h2>⚠️ Confirm {dryRun ? 'Preview' : 'Deletion'}</h2>
            <p>You are about to {dryRun ? 'preview' : 'DELETE'} <strong>{selectedIds.length} resource(s)</strong></p>
            
            <div className="confirmation-details">
              <div className="detail-item">
                <span className="label">Service:</span>
                <span className="value">{results.technique.name}</span>
              </div>
              <div className="detail-item">
                <span className="label">Resources:</span>
                <span className="value">{selectedIds.length} selected</span>
              </div>
              <div className="detail-item">
                <span className="label">Potential Savings:</span>
                <span className="value">
                  ${results.findings
                    .filter(f => selectedIds.includes(f.resource_id))
                    .reduce((sum, f) => sum + f.estimated_savings, 0)
                    .toFixed(2)}/month
                </span>
              </div>
            </div>

            {!dryRun && (
              <div className="confirmation-input">
                <p>⚠️ <strong>This action cannot be undone!</strong></p>
                <p>To confirm, type the service name below:</p>
                <input
                  type="text"
                  placeholder={`Type "${results.technique.name}" to confirm`}
                  value={confirmationInput}
                  onChange={(e) => {
                    setConfirmationInput(e.target.value);
                    setConfirmationError('');
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && confirmationInput) {
                      handleConfirmOptimization();
                    }
                  }}
                  className={confirmationError ? 'error' : ''}
                  autoFocus
                />
                {confirmationError && <span className="error-text">{confirmationError}</span>}
              </div>
            )}

            <div className="confirmation-actions">
              <button
                onClick={() => setShowConfirmation(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              {dryRun ? (
                <button
                  onClick={handleConfirmOptimization}
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Processing...' : 'Preview Optimization'}
                </button>
              ) : (
                <button
                  onClick={handleConfirmOptimization}
                  className="btn btn-danger"
                  disabled={loading || !confirmationInput}
                >
                  {loading ? 'Deleting...' : 'Execute Deletion'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="results-header">
        <button onClick={onBack} className="btn-back">← Back</button>
        <h2>{results.technique.name}</h2>
        <div className="results-stats">
          <div className="stat">
            <span className="stat-label">Resources Found</span>
            <span className="stat-value">{results.count}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Monthly Savings Potential</span>
            <span className="stat-value">${results.total_monthly_savings.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {results.findings.length > 0 ? (
        <>
          <div className="action-bar">
            <div className="mode-selector">
              <label>
                <input
                  type="checkbox"
                  checked={!dryRun}
                  onChange={(e) => setDryRun(!e.target.checked)}
                />
                Execute Changes (⚠️ Live Mode)
              </label>
              {dryRun && <span className="dry-run-badge">🔍 Dry-Run Mode</span>}
            </div>

            <div className="export-buttons">
              <button onClick={exportAsJSON} className="btn btn-small">📄 JSON</button>
              <button onClick={exportAsCSV} className="btn btn-small">📊 CSV</button>
            </div>
          </div>

          <ResourceList
            findings={results.findings}
            selectedIds={selectedIds}
            onSelectAll={handleSelectAll}
            onToggleResource={handleToggleResource}
          />

          {selectedIds.length > 0 && (
            <div className="confirm-section">
              <div className="selected-summary">
                <p>Selected: {selectedIds.length} resources</p>
                <p>
                  Potential Savings: $
                  {results.findings
                    .filter(f => selectedIds.includes(f.resource_id))
                    .reduce((sum, f) => sum + f.estimated_savings, 0)
                    .toFixed(2)}
                  /month
                </p>
              </div>
              <button
                onClick={handleOptimize}
                className="btn btn-danger"
                disabled={loading}
              >
                {loading ? 'Processing...' : `${dryRun ? 'Preview' : 'Execute'} Optimization`}
              </button>
            </div>
          )}

          {results.optimization_results && (
            <div className="optimization-results">
              <h3>Optimization Results</h3>
              <div className="results-summary">
                <span className="success-count">✅ {results.optimization_results.summary.success} Successful</span>
                <span className="failed-count">❌ {results.optimization_results.summary.failed} Failed</span>
              </div>
              <div className="results-list">
                {results.optimization_results.results.map((result, idx) => (
                  <div key={idx} className={`result-item ${result.status}`}>
                    <span className="status-icon">{result.status === 'success' ? '✅' : '❌'}</span>
                    <span className="resource-id">{result.resource_id}</span>
                    <span className="message">{result.message || result.error}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="no-findings">
          <p>🎉 No resources found for optimization!</p>
          <p>Your AWS account is already well-optimized for this technique.</p>
        </div>
      )}
    </div>
  );
}
