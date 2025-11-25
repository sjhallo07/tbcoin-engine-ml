/**
 * TB Coin Engine - Job Model
 * 
 * MongoDB model for jobs/tasks using Mongoose ODM
 */
const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  jobId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  jobType: {
    type: String,
    required: true,
    enum: [
      'transaction',
      'analysis',
      'ml_prediction',
      'blockchain_sync',
      'data_processing',
      'smart_contract',
      'staking',
    ],
    index: true,
  },
  status: {
    type: String,
    enum: ['pending', 'queued', 'running', 'completed', 'failed', 'cancelled'],
    default: 'pending',
    index: true,
  },
  priority: {
    type: Number,
    min: 1,
    max: 10,
    default: 5,
    index: true,
  },
  payload: {
    type: mongoose.Schema.Types.Mixed,
    default: {},
  },
  result: {
    type: mongoose.Schema.Types.Mixed,
    default: null,
  },
  error: {
    type: String,
    default: null,
  },
  startedAt: {
    type: Date,
    default: null,
  },
  completedAt: {
    type: Date,
    default: null,
  },
  createdBy: {
    type: String,
    index: true,
  },
  callbackUrl: {
    type: String,
  },
}, {
  timestamps: true,
});

// Compound index for job queue queries
jobSchema.index({ status: 1, priority: -1, createdAt: 1 });

// Instance method to check if job can be cancelled
jobSchema.methods.canBeCancelled = function() {
  return ['pending', 'queued'].includes(this.status);
};

// Instance method to mark as running
jobSchema.methods.markAsRunning = function() {
  this.status = 'running';
  this.startedAt = new Date();
  return this.save();
};

// Instance method to mark as completed
jobSchema.methods.markAsCompleted = function(result) {
  this.status = 'completed';
  this.result = result;
  this.completedAt = new Date();
  return this.save();
};

// Instance method to mark as failed
jobSchema.methods.markAsFailed = function(error) {
  this.status = 'failed';
  this.error = error;
  this.completedAt = new Date();
  return this.save();
};

// Static method to get next pending job
jobSchema.statics.getNextPending = function() {
  return this.findOneAndUpdate(
    { status: 'pending' },
    { status: 'queued' },
    { 
      sort: { priority: -1, createdAt: 1 },
      new: true,
    }
  );
};

// Static method to get jobs by status
jobSchema.statics.getByStatus = function(status, limit = 100) {
  return this.find({ status })
    .sort({ createdAt: -1 })
    .limit(limit);
};

const Job = mongoose.model('Job', jobSchema);

module.exports = Job;
