/**
 * TB Coin Engine - Routes Index
 */
const healthRoutes = require('./health');
const authRoutes = require('./auth');
const jobRoutes = require('./jobs');

module.exports = {
  healthRoutes,
  authRoutes,
  jobRoutes,
};
