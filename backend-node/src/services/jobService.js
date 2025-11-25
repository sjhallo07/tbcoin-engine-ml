/**
 * TB Coin Engine - Job Execution Service
 * 
 * Handles job execution for various job types in the coin engine
 */
const { v4: uuidv4 } = require('uuid');
const Job = require('../models/Job');
const logger = require('../utils/logger');
const pythonBackendService = require('./pythonBackendService');

class JobService {
  constructor() {
    this.isProcessing = false;
    this.jobHandlers = new Map();
    
    // Register default job handlers
    this.registerHandler('transaction', this.handleTransactionJob.bind(this));
    this.registerHandler('analysis', this.handleAnalysisJob.bind(this));
    this.registerHandler('ml_prediction', this.handleMLPredictionJob.bind(this));
    this.registerHandler('blockchain_sync', this.handleBlockchainSyncJob.bind(this));
    this.registerHandler('data_processing', this.handleDataProcessingJob.bind(this));
    this.registerHandler('smart_contract', this.handleSmartContractJob.bind(this));
    this.registerHandler('staking', this.handleStakingJob.bind(this));
  }

  /**
   * Register a handler for a job type
   * @param {string} jobType - Type of job
   * @param {Function} handler - Handler function
   */
  registerHandler(jobType, handler) {
    this.jobHandlers.set(jobType, handler);
    logger.info(`Registered handler for job type: ${jobType}`);
  }

  /**
   * Create a new job
   * @param {Object} jobData - Job data
   * @returns {Object} Created job
   */
  async createJob(jobData) {
    const job = new Job({
      jobId: `job_${uuidv4().substring(0, 12)}`,
      jobType: jobData.jobType,
      priority: jobData.priority || 5,
      payload: jobData.payload || {},
      createdBy: jobData.createdBy,
      callbackUrl: jobData.callbackUrl,
    });

    await job.save();
    logger.info(`Job created: ${job.jobId}`, { jobType: job.jobType });

    return job;
  }

  /**
   * Execute a specific job
   * @param {string} jobId - Job ID
   * @returns {Object} Job result
   */
  async executeJob(jobId) {
    const job = await Job.findOne({ jobId });
    
    if (!job) {
      throw new Error(`Job not found: ${jobId}`);
    }

    if (!['pending', 'queued'].includes(job.status)) {
      throw new Error(`Job cannot be executed. Status: ${job.status}`);
    }

    const handler = this.jobHandlers.get(job.jobType);
    
    if (!handler) {
      throw new Error(`No handler registered for job type: ${job.jobType}`);
    }

    try {
      await job.markAsRunning();
      logger.info(`Executing job: ${job.jobId}`, { jobType: job.jobType });

      const result = await handler(job);
      
      await job.markAsCompleted(result);
      logger.info(`Job completed: ${job.jobId}`, { jobType: job.jobType });

      // Call callback URL if provided
      if (job.callbackUrl) {
        await this.sendCallback(job.callbackUrl, job);
      }

      return job;
    } catch (error) {
      await job.markAsFailed(error.message);
      logger.error(`Job failed: ${job.jobId}`, { 
        jobType: job.jobType,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Get job by ID
   * @param {string} jobId - Job ID
   * @returns {Object} Job
   */
  async getJob(jobId) {
    return Job.findOne({ jobId });
  }

  /**
   * Get jobs by status
   * @param {string} status - Job status
   * @param {number} limit - Maximum jobs to return
   * @returns {Array} Jobs
   */
  async getJobsByStatus(status, limit = 100) {
    return Job.getByStatus(status, limit);
  }

  /**
   * Cancel a job
   * @param {string} jobId - Job ID
   * @returns {Object} Cancelled job
   */
  async cancelJob(jobId) {
    const job = await Job.findOne({ jobId });
    
    if (!job) {
      throw new Error(`Job not found: ${jobId}`);
    }

    if (!job.canBeCancelled()) {
      throw new Error(`Job cannot be cancelled. Status: ${job.status}`);
    }

    job.status = 'cancelled';
    job.completedAt = new Date();
    await job.save();

    logger.info(`Job cancelled: ${job.jobId}`);
    return job;
  }

  /**
   * Process pending jobs
   */
  async processPendingJobs() {
    if (this.isProcessing) {
      return;
    }

    this.isProcessing = true;

    try {
      while (true) {
        const job = await Job.getNextPending();
        
        if (!job) {
          break;
        }

        try {
          await this.executeJob(job.jobId);
        } catch (error) {
          logger.error(`Error processing job ${job.jobId}:`, error);
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  // Job Handlers

  async handleTransactionJob(job) {
    const result = await pythonBackendService.processTransaction(job.payload);
    return result;
  }

  async handleAnalysisJob(job) {
    // Perform analysis using Python backend
    const result = await pythonBackendService.syncData('analysis', job.payload);
    return result;
  }

  async handleMLPredictionJob(job) {
    const { modelType, features } = job.payload;
    const result = await pythonBackendService.getPrediction(modelType, features);
    return result;
  }

  async handleBlockchainSyncJob(job) {
    const result = await pythonBackendService.syncData('blockchain', job.payload);
    return result;
  }

  async handleDataProcessingJob(job) {
    const result = await pythonBackendService.executeJob({
      type: 'data_processing',
      ...job.payload,
    });
    return result;
  }

  async handleSmartContractJob(job) {
    const result = await pythonBackendService.executeJob({
      type: 'smart_contract',
      ...job.payload,
    });
    return result;
  }

  async handleStakingJob(job) {
    const result = await pythonBackendService.executeJob({
      type: 'staking',
      ...job.payload,
    });
    return result;
  }

  async sendCallback(url, job) {
    try {
      const axios = require('axios');
      await axios.post(url, {
        jobId: job.jobId,
        status: job.status,
        result: job.result,
        error: job.error,
        completedAt: job.completedAt,
      }, {
        timeout: 10000,
      });
      logger.info(`Callback sent for job: ${job.jobId}`);
    } catch (error) {
      logger.warn(`Failed to send callback for job ${job.jobId}:`, error.message);
    }
  }
}

// Export singleton instance
const jobService = new JobService();

module.exports = jobService;
