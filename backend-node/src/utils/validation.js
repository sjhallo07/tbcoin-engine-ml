/**
 * TB Coin Engine - Input Validation and Sanitization Utilities
 * 
 * Provides comprehensive input validation to prevent:
 * - SQL injection
 * - NoSQL injection
 * - XSS attacks
 */
const { body, param, query, validationResult } = require('express-validator');

/**
 * Sanitize string input
 * @param {string} input - Input string to sanitize
 * @returns {string} Sanitized string
 */
function sanitizeString(input) {
  if (typeof input !== 'string') {
    return input;
  }

  return input
    // Remove null bytes
    .replace(/\x00/g, '')
    // Escape HTML entities
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    // Remove potential script tags
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    // Remove event handlers
    .replace(/on\w+\s*=/gi, '');
}

/**
 * Sanitize object recursively
 * @param {Object} obj - Object to sanitize
 * @returns {Object} Sanitized object
 */
function sanitizeObject(obj) {
  if (typeof obj !== 'object' || obj === null) {
    return typeof obj === 'string' ? sanitizeString(obj) : obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item));
  }

  const sanitized = {};
  for (const [key, value] of Object.entries(obj)) {
    // Skip MongoDB operators in keys
    if (key.startsWith('$')) {
      continue;
    }
    sanitized[sanitizeString(key)] = sanitizeObject(value);
  }
  return sanitized;
}

/**
 * Check for NoSQL injection patterns
 * @param {*} value - Value to check
 * @returns {boolean} True if injection pattern detected
 */
function hasNoSQLInjection(value) {
  if (typeof value === 'object' && value !== null) {
    const suspicious = ['$where', '$gt', '$lt', '$ne', '$regex', '$or', '$and', '$nin', '$in'];
    return Object.keys(value).some(key => suspicious.includes(key));
  }
  return false;
}

/**
 * Check for SQL injection patterns
 * @param {string} value - Value to check
 * @returns {boolean} True if injection pattern detected
 */
function hasSQLInjection(value) {
  if (typeof value !== 'string') {
    return false;
  }

  const patterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)/i,
    /(--|;|\/\*|\*\/)/,
    /(\bOR\b\s+\d+\s*=\s*\d+)/i,
    /(\bAND\b\s+\d+\s*=\s*\d+)/i,
    /('.*--)/,
  ];

  return patterns.some(pattern => pattern.test(value));
}

/**
 * Validation middleware for handling validation errors
 */
function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      status: 'error',
      message: 'Validation failed',
      details: errors.array().map(err => ({
        field: err.path,
        message: err.msg,
        value: err.value,
      })),
    });
  }
  next();
}

// Common validation chains
const commonValidators = {
  // User ID validation
  userId: () => param('userId')
    .trim()
    .notEmpty().withMessage('User ID is required')
    .isLength({ min: 1, max: 100 }).withMessage('User ID must be 1-100 characters')
    .matches(/^[a-zA-Z0-9_-]+$/).withMessage('User ID contains invalid characters'),

  // Transaction ID validation
  transactionId: () => param('transactionId')
    .trim()
    .notEmpty().withMessage('Transaction ID is required')
    .isLength({ min: 1, max: 100 }).withMessage('Transaction ID must be 1-100 characters')
    .matches(/^[a-zA-Z0-9_-]+$/).withMessage('Transaction ID contains invalid characters'),

  // Amount validation
  amount: () => body('amount')
    .isFloat({ min: 0.01 }).withMessage('Amount must be a positive number')
    .custom((value) => value <= 1000000).withMessage('Amount exceeds maximum'),

  // Email validation
  email: () => body('email')
    .trim()
    .isEmail().withMessage('Invalid email format')
    .normalizeEmail(),

  // Password validation
  password: () => body('password')
    .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
    .matches(/[A-Z]/).withMessage('Password must contain uppercase letter')
    .matches(/[a-z]/).withMessage('Password must contain lowercase letter')
    .matches(/\d/).withMessage('Password must contain a digit'),

  // Username validation
  username: () => body('username')
    .trim()
    .isLength({ min: 3, max: 50 }).withMessage('Username must be 3-50 characters')
    .matches(/^[a-zA-Z0-9_-]+$/).withMessage('Username contains invalid characters'),

  // Pagination validation
  pagination: () => [
    query('page')
      .optional()
      .isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit')
      .optional()
      .isInt({ min: 1, max: 100 }).withMessage('Limit must be 1-100'),
  ],
};

module.exports = {
  sanitizeString,
  sanitizeObject,
  hasNoSQLInjection,
  hasSQLInjection,
  handleValidationErrors,
  commonValidators,
};
