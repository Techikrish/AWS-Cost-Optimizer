import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import CredentialForm from './components/CredentialForm';
import TechniqueCard from './components/TechniqueCard';
import AnalysisResults from './components/AnalysisResults';
import Header from './components/Header';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [credentials, setCredentials] = useState(null);
  const [techniques, setTechniques] = useState([]);
  const [selectedTechnique, setSelectedTechnique] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dryRun, setDryRun] = useState(true);
  const [showDryRunModal, setShowDryRunModal] = useState(false);

  useEffect(() => {
    fetchTechniques();
    checkCredentials();
  }, []);

  const fetchTechniques = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/techniques`);
      setTechniques(response.data);
    } catch (err) {
      console.error('Failed to fetch techniques:', err);
    }
  };

  const checkCredentials = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/credentials/check`);
      if (response.data.valid) {
        setCredentials(response.data);
      }
    } catch (err) {
      // No credentials saved yet
    }
  };

  const handleCredentialsSubmit = async (creds) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/credentials/validate`, creds);
      setCredentials(response.data);
      setError(null);
      setShowDryRunModal(true); // Show dry-run modal after successful credentials
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to validate credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (technique) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze/${technique.id}`, {
        region: 'us-east-1'
      });
      setAnalysisResults({ ...response.data, technique });
      setSelectedTechnique(technique);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze resources');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async (resourceIds) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/optimize/${selectedTechnique.id}`, {
        resource_ids: resourceIds,
        dry_run: dryRun,
        region: 'us-east-1'
      });
      setAnalysisResults(prev => ({
        ...prev,
        optimization_results: response.data
      }));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to optimize resources');
    } finally {
      setLoading(false);
    }
  };

  const handleClearCredentials = async () => {
    try {
      await axios.post(`${API_BASE_URL}/credentials/clear`);
      setCredentials(null);
      setAnalysisResults(null);
      setSelectedTechnique(null);
      setShowDryRunModal(false);
    } catch (err) {
      console.error('Failed to clear credentials:', err);
    }
  };

  const handleStartAnalysis = (dryRunMode) => {
    setDryRun(dryRunMode);
    setShowDryRunModal(false);
    // Go to technique selection
  };

  if (!credentials) {
    return (
      <div className="app">
        <Header onLogout={handleClearCredentials} loggedIn={false} />
        <div className="container">
          <div className="welcome-section">
            <h1>🔧 AWS Cost Optimizer</h1>
            <p>Reduce your AWS costs with 15 powerful optimization techniques</p>
            <CredentialForm onSubmit={handleCredentialsSubmit} loading={loading} error={error} />
          </div>
        </div>
      </div>
    );
  }

  // Show dry-run confirmation modal
  if (showDryRunModal) {
    return (
      <div className="app">
        <Header onLogout={handleClearCredentials} loggedIn={true} user={credentials.user} />
        <div className="container">
          <div className="modal-overlay">
            <div className="dry-run-modal">
              <h2>⚙️ Analysis Mode Selection</h2>
              <p>How would you like to analyze your AWS resources?</p>
              
              <div className="mode-options">
                <div className="mode-card dry-run-card">
                  <h3>🔍 Dry-Run Mode (Recommended)</h3>
                  <p>Preview what would be deleted without making any changes</p>
                  <ul>
                    <li>✅ Safe preview of resources</li>
                    <li>✅ No actual deletions occur</li>
                    <li>✅ Review costs and details first</li>
                    <li>✅ Perfect for first-time users</li>
                  </ul>
                  <button 
                    onClick={() => handleStartAnalysis(true)} 
                    className="btn btn-primary"
                  >
                    Start Analysis (Dry-Run)
                  </button>
                </div>

                <div className="mode-card live-card">
                  <h3>⚡ Live Mode</h3>
                  <p>Actually delete resources (⚠️ Use with caution)</p>
                  <ul>
                    <li>⚠️ Resources will be deleted</li>
                    <li>⚠️ Requires additional confirmation</li>
                    <li>⚠️ For experienced users only</li>
                    <li>⚠️ Always review carefully first</li>
                  </ul>
                  <button 
                    onClick={() => handleStartAnalysis(false)} 
                    className="btn btn-danger"
                  >
                    Start Analysis (Live)
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header onLogout={handleClearCredentials} loggedIn={true} user={credentials.user} />
      <div className="container">
        {error && <div className="error-banner">{error}</div>}
        
        {!analysisResults ? (
          <div className="techniques-grid">
            <h2>Select Optimization Technique</h2>
            <div className="grid">
              {techniques.map(technique => (
                <TechniqueCard
                  key={technique.id}
                  technique={technique}
                  onAnalyze={handleAnalyze}
                  loading={loading}
                />
              ))}
            </div>
          </div>
        ) : (
          <AnalysisResults
            results={analysisResults}
            onOptimize={handleOptimize}
            onBack={() => setAnalysisResults(null)}
            dryRun={dryRun}
            setDryRun={setDryRun}
            loading={loading}
          />
        )}
      </div>
      <footer className="app-footer">
        <p>Made with ❤️ by <strong>techikrish</strong> | AWS Cost Optimizer v1.1</p>
      </footer>
    </div>
  );
}

export default App;
