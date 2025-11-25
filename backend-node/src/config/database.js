/**
 * TB Coin Engine - MongoDB Connection Module
 * 
 * Provides MongoDB connection with:
 * - Connection pooling
 * - Reconnection handling
 * - Health monitoring
 */
const mongoose = require('mongoose');
const config = require('./index');
const logger = require('../utils/logger');

class Database {
  constructor() {
    this.isConnected = false;
    this.connectionAttempts = 0;
    this.maxRetries = 5;
  }

  /**
   * Connect to MongoDB with retry logic
   */
  async connect() {
    if (this.isConnected) {
      logger.info('MongoDB already connected');
      return;
    }

    try {
      this.connectionAttempts++;
      
      await mongoose.connect(config.mongodb.uri, config.mongodb.options);
      
      this.isConnected = true;
      this.connectionAttempts = 0;
      logger.info('MongoDB connected successfully');

      // Set up connection event handlers
      this.setupEventHandlers();
      
    } catch (error) {
      logger.error(`MongoDB connection failed (attempt ${this.connectionAttempts}):`, error);
      
      if (this.connectionAttempts < this.maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, this.connectionAttempts), 30000);
        logger.info(`Retrying MongoDB connection in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.connect();
      }
      
      throw error;
    }
  }

  /**
   * Set up MongoDB connection event handlers
   */
  setupEventHandlers() {
    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB disconnected');
      this.isConnected = false;
    });

    mongoose.connection.on('error', (error) => {
      logger.error('MongoDB connection error:', error);
    });

    mongoose.connection.on('reconnected', () => {
      logger.info('MongoDB reconnected');
      this.isConnected = true;
    });
  }

  /**
   * Disconnect from MongoDB
   */
  async disconnect() {
    if (!this.isConnected) {
      return;
    }

    try {
      await mongoose.disconnect();
      this.isConnected = false;
      logger.info('MongoDB disconnected');
    } catch (error) {
      logger.error('Error disconnecting from MongoDB:', error);
      throw error;
    }
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      readyState: mongoose.connection.readyState,
      host: mongoose.connection.host,
      name: mongoose.connection.name,
    };
  }
}

// Export singleton instance
const database = new Database();

module.exports = database;
