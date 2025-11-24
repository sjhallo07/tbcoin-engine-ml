/**
 * TB Coin Engine - Node.js Backend Configuration
 * 
 * Centralized configuration using environment variables
 * following security best practices.
 */
require('dotenv').config();

const config = {
  // Application settings
  app: {
    name: process.env.APP_NAME || 'TB Coin Backend Node',
    env: process.env.NODE_ENV || 'development',
    port: parseInt(process.env.NODE_PORT || '3000', 10),
    host: process.env.NODE_HOST || '0.0.0.0',
  },

  // Security settings
  security: {
    jwtSecret: process.env.JWT_SECRET_KEY || 'change-this-jwt-secret',
    jwtExpiry: process.env.JWT_EXPIRY || '1h',
    apiKey: process.env.API_KEY || '',
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '10', 10),
  },

  // MongoDB settings
  mongodb: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/tbcoin',
    options: {
      maxPoolSize: parseInt(process.env.MONGODB_MAX_POOL_SIZE || '100', 10),
      minPoolSize: parseInt(process.env.MONGODB_MIN_POOL_SIZE || '10', 10),
      serverSelectionTimeoutMS: parseInt(process.env.MONGODB_TIMEOUT_MS || '5000', 10),
    },
  },

  // Python backend settings (for synchronization)
  pythonBackend: {
    url: process.env.PYTHON_BACKEND_URL || 'http://localhost:8000',
    timeout: parseInt(process.env.PYTHON_BACKEND_TIMEOUT || '30000', 10),
  },

  // Rate limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
    max: parseInt(process.env.RATE_LIMIT_MAX || '60', 10),
  },

  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
  },

  // CORS settings
  cors: {
    origins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3001'],
    credentials: true,
  },
};

// Validate required configuration
function validateConfig() {
  const errors = [];

  if (config.app.env === 'production') {
    if (config.security.jwtSecret === 'change-this-jwt-secret') {
      errors.push('JWT_SECRET_KEY must be set in production');
    }
    // Validate JWT secret meets minimum security requirements
    if (config.security.jwtSecret.length < 32) {
      errors.push('JWT_SECRET_KEY must be at least 32 characters for security');
    }
  }

  if (errors.length > 0) {
    throw new Error(`Configuration errors:\n${errors.join('\n')}`);
  }
}

// Only validate in production
if (config.app.env === 'production') {
  validateConfig();
}

module.exports = config;
