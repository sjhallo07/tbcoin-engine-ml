/**
 * TB Coin Engine - Job Routes
 */
const express = require('express');
const router = express.Router();
const { body, param } = require('express-validator');
const { asyncHandler } = require('../middleware/errorHandler');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { handleValidationErrors } = require('../utils/validation');
const jobService = require('../services/jobService');

/**
 * @route POST /api/v1/jobs
 * @desc Create a new job
 * @access Private
 */
router.post('/',
  authenticateToken,
  [
    body('jobType')
      .isIn(['transaction', 'analysis', 'ml_prediction', 'blockchain_sync', 'data_processing', 'smart_contract', 'staking'])
      .withMessage('Invalid job type'),
    body('priority')
      .optional()
      .isInt({ min: 1, max: 10 })
      .withMessage('Priority must be 1-10'),
    body('payload')
      .optional()
      .isObject()
      .withMessage('Payload must be an object'),
    body('callbackUrl')
      .optional()
      .isURL()
      .withMessage('Invalid callback URL'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const job = await jobService.createJob({
      ...req.body,
      createdBy: req.user.id,
    });

    res.status(201).json({
      status: 'success',
      message: 'Job created successfully',
      data: job,
    });
  })
);

/**
 * @route GET /api/v1/jobs/:jobId
 * @desc Get job by ID
 * @access Private
 */
router.get('/:jobId',
  authenticateToken,
  [
    param('jobId')
      .matches(/^job_[a-zA-Z0-9]+$/)
      .withMessage('Invalid job ID format'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const job = await jobService.getJob(req.params.jobId);

    if (!job) {
      return res.status(404).json({
        status: 'error',
        message: 'Job not found',
      });
    }

    res.json({
      status: 'success',
      data: job,
    });
  })
);

/**
 * @route POST /api/v1/jobs/:jobId/execute
 * @desc Execute a job
 * @access Private (Operator+)
 */
router.post('/:jobId/execute',
  authenticateToken,
  requireRole('operator', 'admin'),
  [
    param('jobId')
      .matches(/^job_[a-zA-Z0-9]+$/)
      .withMessage('Invalid job ID format'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const job = await jobService.executeJob(req.params.jobId);

    res.json({
      status: 'success',
      message: 'Job executed successfully',
      data: job,
    });
  })
);

/**
 * @route POST /api/v1/jobs/:jobId/cancel
 * @desc Cancel a job
 * @access Private
 */
router.post('/:jobId/cancel',
  authenticateToken,
  [
    param('jobId')
      .matches(/^job_[a-zA-Z0-9]+$/)
      .withMessage('Invalid job ID format'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const job = await jobService.cancelJob(req.params.jobId);

    res.json({
      status: 'success',
      message: 'Job cancelled successfully',
      data: job,
    });
  })
);

/**
 * @route GET /api/v1/jobs/status/:status
 * @desc Get jobs by status
 * @access Private (Operator+)
 */
router.get('/status/:status',
  authenticateToken,
  requireRole('operator', 'admin'),
  [
    param('status')
      .isIn(['pending', 'queued', 'running', 'completed', 'failed', 'cancelled'])
      .withMessage('Invalid status'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const jobs = await jobService.getJobsByStatus(req.params.status);

    res.json({
      status: 'success',
      data: jobs,
      count: jobs.length,
    });
  })
);

module.exports = router;
