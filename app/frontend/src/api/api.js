const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = {
  // Health check
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('API health check failed');
    return response.json();
  },

  // Get home info
  async getHome() {
    const response = await fetch(`${API_BASE_URL}/home`);
    if (!response.ok) throw new Error('Failed to fetch home info');
    return response.json();
  },

  // Get about info
  async getAbout() {
    const response = await fetch(`${API_BASE_URL}/about`);
    if (!response.ok) throw new Error('Failed to fetch about info');
    return response.json();
  },

  // Analyze content (Cross-reference check)
  async analyze(title, content) {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, content }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Analysis failed');
    }
    return response.json();
  },

  // Get trusted sources
  async getSources() {
    const response = await fetch(`${API_BASE_URL}/sources`);
    if (!response.ok) throw new Error('Failed to fetch sources');
    return response.json();
  },

  // Get weights configuration
  async getWeights() {
    const response = await fetch(`${API_BASE_URL}/weights`);
    if (!response.ok) throw new Error('Failed to fetch weights');
    return response.json();
  },
};

export default api;