/**
 * TB Coin Engine - Error Handling Middleware
 * 
 * Provides comprehensive error handling with:
 * - Structured error responses
 * - Error logging
 * - Different handling for production vs development
 */
const logger = require('../utils/logger');
const config = require('../config');

/**
 * Custom error class for application errors
 */
class AppError extends Error {
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Validation error class
 */
class ValidationError extends AppError {
  constructor(message, details = []) {
    super(message, 400, 'VALIDATION_ERROR');
    this.details = details;
  }
}

/**
 * Not found error class
 */
class NotFoundError extends AppError {
  constructor(resource, identifier = null) {
    const message = identifier
      ? `${resource} with ID '${identifier}' not found`
      : `${resource} not found`;
    super(message, 404, 'NOT_FOUND');
  }
}

/**
 * Authentication error class
 */
class AuthenticationError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 401, 'AUTHENTICATION_ERROR');
  }
}

/**
 * Authorization error class
 */
class AuthorizationError extends AppError {
  constructor(message = 'Access denied') {
    super(message, 403, 'AUTHORIZATION_ERROR');
  }
}

/**
 * Handle 404 errors (route not found)
 */
function notFoundHandler(req, res, next) {
  const error = new NotFoundError('Route', `${req.method} ${req.originalUrl}`);
  next(error);
}

/**
 * Global error handler middleware
 */
function errorHandler(err, req, res, next) {
  // Log the error
  const requestId = req.id || 'unknown';
  
  if (err.isOperational) {
    logger.warn('Operational error:', {
      requestId,
      code: err.code,
      message: err.message,
      statusCode: err.statusCode,
    });
  } else {
    logger.error('Unexpected error:', {
      requestId,
      error: err.message,
      stack: err.stack,
    });
  }

  // Determine status code
  const statusCode = err.statusCode || 500;
  
  // Build error response
  const errorResponse = {
    status: 'error',
    message: err.isOperational ? err.message : 'An unexpected error occurred',
    code: err.code || 'INTERNAL_ERROR',
    requestId,
    timestamp: new Date().toISOString(),
  };

  // Add details for validation errors
  if (err.details && Array.isArray(err.details)) {
    errorResponse.details = err.details;
  }

  // Add stack trace in development
  if (config.app.env === 'development' && !err.isOperational) {
    errorResponse.stack = err.stack;
  }

  res.status(statusCode).json(errorResponse);
}

/**
 * Async handler wrapper to catch async errors
 * @param {Function} fn - Async route handler
 * @returns {Function} Wrapped handler
 */
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = {
  AppError,
  ValidationError,
  NotFoundError,
  AuthenticationError,
  AuthorizationError,
  notFoundHandler,
  errorHandler,
  asyncHandler,
};
