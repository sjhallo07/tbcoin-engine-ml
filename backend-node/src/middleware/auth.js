/**
 * TB Coin Engine - Authentication Middleware
 * 
 * Provides JWT authentication and role-based access control (RBAC)
 */
const jwt = require('jsonwebtoken');
const config = require('../config');
const logger = require('../utils/logger');

// Role hierarchy for RBAC
const roleHierarchy = {
  admin: ['admin', 'operator', 'user', 'viewer'],
  operator: ['operator', 'user', 'viewer'],
  user: ['user', 'viewer'],
  viewer: ['viewer'],
};

/**
 * Verify JWT token and attach user to request
 */
function authenticateToken(req, res, next) {
  // Get token from Authorization header
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  // Also check for API key authentication
  const apiKey = req.headers['x-api-key'];
  
  if (!token && !apiKey) {
    return res.status(401).json({
      status: 'error',
      message: 'Authentication required',
    });
  }

  // Handle API key authentication
  if (apiKey) {
    if (apiKey === config.security.apiKey) {
      req.user = {
        id: 'system',
        username: 'api_user',
        role: 'operator',
      };
      return next();
    }
    return res.status(401).json({
      status: 'error',
      message: 'Invalid API key',
    });
  }

  // Handle JWT authentication
  try {
    const decoded = jwt.verify(token, config.security.jwtSecret);
    req.user = {
      id: decoded.sub,
      username: decoded.username,
      role: decoded.role || 'user',
    };
    next();
  } catch (error) {
    logger.warn('JWT verification failed:', { error: error.message });
    return res.status(401).json({
      status: 'error',
      message: 'Invalid or expired token',
    });
  }
}

/**
 * Optional authentication - doesn't fail if no token
 */
function optionalAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    req.user = null;
    return next();
  }

  try {
    const decoded = jwt.verify(token, config.security.jwtSecret);
    req.user = {
      id: decoded.sub,
      username: decoded.username,
      role: decoded.role || 'user',
    };
  } catch (error) {
    req.user = null;
  }
  
  next();
}

/**
 * Create role-based access control middleware
 * @param {string[]} allowedRoles - Roles allowed to access the route
 */
function requireRole(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        status: 'error',
        message: 'Authentication required',
      });
    }

    const userRole = req.user.role;
    const effectiveRoles = roleHierarchy[userRole] || [];
    
    const hasAccess = allowedRoles.some(role => effectiveRoles.includes(role));
    
    if (!hasAccess) {
      logger.warn('Access denied:', {
        userId: req.user.id,
        userRole,
        requiredRoles: allowedRoles,
      });
      return res.status(403).json({
        status: 'error',
        message: 'Access denied. Insufficient permissions.',
      });
    }

    next();
  };
}

/**
 * Generate JWT token for user
 * @param {Object} user - User object
 * @returns {string} JWT token
 */
function generateToken(user) {
  return jwt.sign(
    {
      sub: user.id,
      username: user.username,
      role: user.role,
    },
    config.security.jwtSecret,
    { expiresIn: config.security.jwtExpiry }
  );
}

/**
 * Generate refresh token
 * @param {Object} user - User object
 * @returns {string} Refresh token
 */
function generateRefreshToken(user) {
  return jwt.sign(
    {
      sub: user.id,
      type: 'refresh',
    },
    config.security.jwtSecret,
    { expiresIn: '7d' }
  );
}

module.exports = {
  authenticateToken,
  optionalAuth,
  requireRole,
  generateToken,
  generateRefreshToken,
};
