import React from 'react';

export default function ResourceList({ findings, selectedIds, onSelectAll, onToggleResource }) {
  return (
    <div className="resource-list">
      <div className="list-header">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={selectedIds.length === findings.length && findings.length > 0}
            onChange={onSelectAll}
          />
          <span>Select All</span>
        </label>
      </div>

      <div className="list-content">
        {findings.map(finding => (
          <div key={finding.resource_id} className="resource-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedIds.includes(finding.resource_id)}
                onChange={() => onToggleResource(finding.resource_id)}
              />
            </label>

            <div className="resource-info">
              <div className="resource-header">
                <span className="resource-id">{finding.resource_id}</span>
                <span className="resource-type">{finding.resource_type}</span>
              </div>

              <div className="resource-details">
                {Object.entries(finding.details).map(([key, value]) => (
                  <div key={key} className="detail-row">
                    <span className="detail-key">{key}:</span>
                    <span className="detail-value">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="resource-savings">
                {finding.estimated_savings > 0 && (
                  <span className="saving-amount">
                    💵 ${finding.estimated_savings.toFixed(2)}/month
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
