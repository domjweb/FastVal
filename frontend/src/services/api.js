import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const claimService = {
  // Upload claim file
  uploadClaim: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/claims/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all claims
  getClaims: async (params = {}) => {
    const response = await api.get('/claims', { params });
    return response.data;
  },

  // Get single claim
  getClaim: async (claimId) => {
    const response = await api.get(`/claims/${claimId}`);
    return response.data;
  },

  // Update claim status
  updateClaimStatus: async (claimId, data) => {
    const response = await api.patch(`/claims/${claimId}/status`, data);
    return response.data;
  },

  // Adjudicate claim
  adjudicateClaim: async (claimId, data) => {
    const response = await api.post(`/claims/${claimId}/adjudicate`, data);
    return response.data;
  },

  // Delete claim
  deleteClaim: async (claimId) => {
    const response = await api.delete(`/claims/${claimId}`);
    return response.data;
  },
};

export const remittanceService = {
  // Get remittance for claim
  getRemittance: async (claimId) => {
    const response = await api.get(`/remittance/${claimId}`);
    return response.data;
  },

  // Get 835 file
  get835File: async (claimId) => {
    const response = await api.get(`/remittance/${claimId}/835`);
    return response.data;
  },
};

export const healthService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
