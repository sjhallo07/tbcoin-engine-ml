/**
 * TB Coin Engine - Python Backend Sync Service
 * 
 * Handles synchronization with the Python backend
 */
const axios = require('axios');
const config = require('../config');
const logger = require('../utils/logger');

class PythonBackendService {
  constructor() {
    this.client = axios.create({
      baseURL: config.pythonBackend.url,
      timeout: config.pythonBackend.timeout,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': config.security.apiKey,
      },
    });

    // Add request/response interceptors for logging
    this.client.interceptors.request.use(
      (config) => {
        logger.debug('Python backend request:', {
          method: config.method,
          url: config.url,
        });
        return config;
      },
      (error) => {
        logger.error('Python backend request error:', error);
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response) => {
        logger.debug('Python backend response:', {
          status: response.status,
          url: response.config.url,
        });
        return response;
      },
      (error) => {
        logger.error('Python backend response error:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Check health of Python backend
   */
  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return {
        healthy: true,
        data: response.data,
      };
    } catch (error) {
      return {
        healthy: false,
        error: error.message,
      };
    }
  }

  /**
   * Get status from Python backend
   */
  async getStatus() {
    try {
      const response = await this.client.get('/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get status: ${error.message}`);
    }
  }

  /**
   * Send transaction to Python backend for processing
   */
  async processTransaction(transaction) {
    try {
      const response = await this.client.post('/api/v1/transactions', transaction);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to process transaction: ${error.message}`);
    }
  }

  /**
   * Execute a job on Python backend
   */
  async executeJob(job) {
    try {
      const response = await this.client.post('/api/v1/jobs/execute', job);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to execute job: ${error.message}`);
    }
  }

  /**
   * Get ML prediction from Python backend
   */
  async getPrediction(modelType, features) {
    try {
      const response = await this.client.post('/api/v1/ml/predict', {
        model_type: modelType,
        features,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get prediction: ${error.message}`);
    }
  }

  /**
   * Sync data with Python backend
   */
  async syncData(dataType, data) {
    try {
      const response = await this.client.post(`/api/v1/sync/${dataType}`, data);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to sync data: ${error.message}`);
    }
  }
}

// Export singleton instance
const pythonBackendService = new PythonBackendService();

module.exports = pythonBackendService;
