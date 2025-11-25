/**
 * TB Coin Engine - Health Routes
 */
const express = require('express');
const router = express.Router();
const database = require('../config/database');
const pythonBackendService = require('../services/pythonBackendService');

/**
 * @route GET /health
 * @desc Health check endpoint
 */
router.get('/', async (req, res) => {
  const pythonHealth = await pythonBackendService.checkHealth();
  
  res.json({
    status: 'healthy',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    services: {
      node_api: 'operational',
      mongodb: database.isConnected ? 'connected' : 'disconnected',
      python_backend: pythonHealth.healthy ? 'connected' : 'disconnected',
    },
  });
});

/**
 * @route GET /health/live
 * @desc Kubernetes liveness probe
 */
router.get('/live', (req, res) => {
  res.json({ status: 'alive' });
});

/**
 * @route GET /health/ready
 * @desc Kubernetes readiness probe
 */
router.get('/ready', (req, res) => {
  if (!database.isConnected) {
    return res.status(503).json({ 
      status: 'not_ready',
      reason: 'Database not connected',
    });
  }
  
  res.json({ status: 'ready' });
});

module.exports = router;
