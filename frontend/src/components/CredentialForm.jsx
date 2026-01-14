import React, { useState } from 'react';

export default function CredentialForm({ onSubmit, loading, error }) {
  const [formData, setFormData] = useState({
    access_key: '',
    secret_key: '',
    region: 'us-east-1'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="credential-form">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>AWS Access Key ID *</label>
          <input
            type="text"
            name="access_key"
            value={formData.access_key}
            onChange={handleChange}
            placeholder="AKIA..."
            required
          />
        </div>

        <div className="form-group">
          <label>AWS Secret Access Key *</label>
          <input
            type="password"
            name="secret_key"
            value={formData.secret_key}
            onChange={handleChange}
            placeholder="Enter your secret access key"
            required
          />
        </div>

        <div className="form-group">
          <label>AWS Region</label>
          <select name="region" value={formData.region} onChange={handleChange}>
            <option value="us-east-1">US East (N. Virginia)</option>
            <option value="us-west-2">US West (Oregon)</option>
            <option value="eu-west-1">Europe (Ireland)</option>
            <option value="eu-central-1">Europe (Frankfurt)</option>
            <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
            <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Validating...' : 'Connect AWS Account'}
        </button>
      </form>

      <div className="security-notice">
        <h3>🔐 Security</h3>
        <ul>
          <li>Credentials are encrypted locally on your machine</li>
          <li>Never stored on remote servers</li>
          <li>Always use IAM keys, not root credentials</li>
          <li>For best practice, attach minimal required permissions policy</li>
        </ul>
      </div>
    </div>
  );
}
