/**
 * TB Coin Engine - Transaction Model
 * 
 * MongoDB model for transactions using Mongoose ODM
 */
const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  transactionId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  transactionHash: {
    type: String,
    unique: true,
    sparse: true,
  },
  chain: {
    type: String,
    default: 'internal',
  },
  fromUser: {
    type: String,
    required: true,
    index: true,
  },
  toUser: {
    type: String,
    required: true,
    index: true,
  },
  amount: {
    type: Number,
    required: true,
    min: 0,
  },
  fee: {
    type: Number,
    default: 0,
    min: 0,
  },
  transactionType: {
    type: String,
    enum: ['send', 'receive', 'mint', 'burn', 'stake', 'unstake', 'swap'],
    default: 'send',
  },
  status: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed', 'cancelled'],
    default: 'pending',
    index: true,
  },
  blockNumber: {
    type: Number,
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {},
  },
}, {
  timestamps: true,
});

// Compound indexes for common queries
transactionSchema.index({ fromUser: 1, createdAt: -1 });
transactionSchema.index({ toUser: 1, createdAt: -1 });
transactionSchema.index({ status: 1, createdAt: 1 });

// Instance method to check if transaction can be cancelled
transactionSchema.methods.canBeCancelled = function() {
  return this.status === 'pending';
};

// Static method to get user transactions
transactionSchema.statics.getUserTransactions = function(userId, limit = 100) {
  return this.find({
    $or: [{ fromUser: userId }, { toUser: userId }]
  })
    .sort({ createdAt: -1 })
    .limit(limit);
};

// Static method to get pending transactions
transactionSchema.statics.getPending = function() {
  return this.find({ status: 'pending' }).sort({ createdAt: 1 });
};

const Transaction = mongoose.model('Transaction', transactionSchema);

module.exports = Transaction;
