/**
 * TB Coin Engine - Request Logging Middleware
 * 
 * Provides comprehensive request logging with:
 * - Request ID tracking
 * - Performance metrics
 * - Structured logging
 */
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');

/**
 * Add request ID to each request
 */
function requestId(req, res, next) {
  req.id = req.headers['x-request-id'] || uuidv4().substring(0, 8);
  res.setHeader('X-Request-ID', req.id);
  next();
}

/**
 * Log request details
 */
function requestLogger(req, res, next) {
  const startTime = Date.now();
  
  // Log request start
  logger.info('Request started', {
    requestId: req.id,
    method: req.method,
    path: req.path,
    query: Object.keys(req.query).length > 0 ? req.query : undefined,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('User-Agent'),
  });

  // Log response when finished
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    
    const logData = {
      requestId: req.id,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
    };

    if (res.statusCode >= 500) {
      logger.error('Request completed with error', logData);
    } else if (res.statusCode >= 400) {
      logger.warn('Request completed with client error', logData);
    } else {
      logger.info('Request completed', logData);
    }

    // Log slow requests
    if (duration > 1000) {
      logger.warn('Slow request detected', { ...logData, threshold: '1000ms' });
    }
  });

  next();
}

/**
 * Security headers middleware
 */
function securityHeaders(req, res, next) {
  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');
  
  // Prevent MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');
  
  // XSS protection
  res.setHeader('X-XSS-Protection', '1; mode=block');
  
  // HTTPS enforcement
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  
  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  // Content Security Policy
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  
  next();
}

module.exports = {
  requestId,
  requestLogger,
  securityHeaders,
};
