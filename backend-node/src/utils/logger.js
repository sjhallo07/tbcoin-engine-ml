/**
 * TB Coin Engine - Winston Logger
 * 
 * Provides structured logging with:
 * - Multiple log levels
 * - JSON formatting for production
 * - Console output for development
 * - Request context tracking
 */
const winston = require('winston');
const config = require('../config');

// Custom log format for development
const devFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
    return `${timestamp} [${level}]: ${message} ${metaStr}`;
  })
);

// Custom log format for production (JSON)
const prodFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.json()
);

// Create logger instance
const logger = winston.createLogger({
  level: config.logging.level,
  format: config.app.env === 'production' ? prodFormat : devFormat,
  defaultMeta: { service: config.app.name },
  transports: [
    new winston.transports.Console(),
  ],
});

// Add file transport in production
if (config.app.env === 'production') {
  logger.add(new winston.transports.File({
    filename: 'logs/error.log',
    level: 'error',
  }));
  logger.add(new winston.transports.File({
    filename: 'logs/combined.log',
  }));
}

/**
 * Create a child logger with request context
 * @param {string} requestId - Request ID for tracking
 * @returns {winston.Logger} Child logger with context
 */
logger.child = (context) => {
  return winston.createLogger({
    level: config.logging.level,
    format: config.app.env === 'production' ? prodFormat : devFormat,
    defaultMeta: { service: config.app.name, ...context },
    transports: [
      new winston.transports.Console(),
    ],
  });
};

module.exports = logger;
