/**
 * TB Coin Engine - Node.js Backend Entry Point
 * 
 * Main Express.js application that:
 * - Provides REST API for job execution
 * - Synchronizes with Python backend
 * - Handles authentication and authorization
 * - Implements security best practices
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');

const config = require('./config');
const database = require('./config/database');
const logger = require('./utils/logger');
const { requestId, requestLogger, securityHeaders } = require('./middleware/requestLogger');
const { notFoundHandler, errorHandler } = require('./middleware/errorHandler');
const { healthRoutes, authRoutes, jobRoutes } = require('./routes');

// Create Express app
const app = express();

// Trust proxy (for rate limiting behind reverse proxy)
app.set('trust proxy', 1);

// ============================================================================
// Security Middleware
// ============================================================================

// Helmet for security headers
app.use(helmet());

// Custom security headers
app.use(securityHeaders);

// CORS configuration
app.use(cors({
  origin: config.cors.origins,
  credentials: config.cors.credentials,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'X-Request-ID'],
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.max,
  message: {
    status: 'error',
    message: 'Too many requests, please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// ============================================================================
// Request Processing Middleware
// ============================================================================

// Request ID tracking
app.use(requestId);

// Request logging
app.use(requestLogger);

// HTTP request logging (Morgan)
if (config.app.env === 'development') {
  app.use(morgan('dev'));
}

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Response compression
app.use(compression());

// ============================================================================
// Routes
// ============================================================================

// Health check routes
app.use('/health', healthRoutes);

// API routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/jobs', jobRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'TB Coin Engine - Node.js Backend',
    version: '1.0.0',
    status: 'operational',
    docs: '/api/docs',
    endpoints: {
      health: '/health',
      auth: '/api/v1/auth',
      jobs: '/api/v1/jobs',
    },
  });
});

// ============================================================================
// Error Handling
// ============================================================================

// 404 handler
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// ============================================================================
// Server Startup
// ============================================================================

async function startServer() {
  try {
    // Connect to MongoDB
    await database.connect();

    // Start HTTP server
    const server = app.listen(config.app.port, config.app.host, () => {
      logger.info(`🚀 ${config.app.name} started`, {
        port: config.app.port,
        host: config.app.host,
        env: config.app.env,
      });
    });

    // Graceful shutdown
    process.on('SIGTERM', async () => {
      logger.info('SIGTERM received. Shutting down gracefully...');
      
      server.close(() => {
        logger.info('HTTP server closed');
      });

      await database.disconnect();
      process.exit(0);
    });

    process.on('SIGINT', async () => {
      logger.info('SIGINT received. Shutting down gracefully...');
      
      server.close(() => {
        logger.info('HTTP server closed');
      });

      await database.disconnect();
      process.exit(0);
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Start the server
startServer();

// Export for testing
module.exports = app;
