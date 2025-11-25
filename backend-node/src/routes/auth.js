/**
 * TB Coin Engine - Auth Routes
 */
const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const { asyncHandler } = require('../middleware/errorHandler');
const { authenticateToken, generateToken, generateRefreshToken } = require('../middleware/auth');
const { handleValidationErrors, commonValidators } = require('../utils/validation');
const User = require('../models/User');

/**
 * @route POST /api/v1/auth/register
 * @desc Register a new user
 * @access Public
 */
router.post('/register',
  [
    commonValidators.username(),
    commonValidators.email(),
    commonValidators.password(),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const { username, email, password } = req.body;

    // Check if user exists
    const existingUser = await User.findOne({
      $or: [{ email }, { username }],
    });

    if (existingUser) {
      return res.status(409).json({
        status: 'error',
        message: existingUser.email === email 
          ? 'Email already registered' 
          : 'Username already taken',
      });
    }

    // Create user
    const user = new User({
      username,
      email,
      password,
    });

    await user.save();

    // Generate tokens
    const accessToken = generateToken(user);
    const refreshToken = generateRefreshToken(user);

    res.status(201).json({
      status: 'success',
      message: 'User registered successfully',
      data: {
        user: user.toPublicJSON(),
        accessToken,
        refreshToken,
      },
    });
  })
);

/**
 * @route POST /api/v1/auth/login
 * @desc Login user
 * @access Public
 */
router.post('/login',
  [
    body('email').isEmail().withMessage('Valid email required'),
    body('password').notEmpty().withMessage('Password required'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    // Find user and verify password
    const user = await User.findByCredentials(email, password);

    if (!user) {
      return res.status(401).json({
        status: 'error',
        message: 'Invalid credentials',
      });
    }

    if (!user.isActive) {
      return res.status(403).json({
        status: 'error',
        message: 'Account is deactivated',
      });
    }

    // Update last login
    user.lastLogin = new Date();
    await user.save();

    // Generate tokens
    const accessToken = generateToken(user);
    const refreshToken = generateRefreshToken(user);

    res.json({
      status: 'success',
      message: 'Login successful',
      data: {
        user: user.toPublicJSON(),
        accessToken,
        refreshToken,
      },
    });
  })
);

/**
 * @route GET /api/v1/auth/me
 * @desc Get current user profile
 * @access Private
 */
router.get('/me',
  authenticateToken,
  asyncHandler(async (req, res) => {
    const user = await User.findById(req.user.id);

    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }

    res.json({
      status: 'success',
      data: user.toPublicJSON(),
    });
  })
);

/**
 * @route POST /api/v1/auth/refresh
 * @desc Refresh access token
 * @access Public (with refresh token)
 */
router.post('/refresh',
  [
    body('refreshToken').notEmpty().withMessage('Refresh token required'),
    handleValidationErrors,
  ],
  asyncHandler(async (req, res) => {
    const { refreshToken } = req.body;
    const jwt = require('jsonwebtoken');
    const config = require('../config');

    try {
      const decoded = jwt.verify(refreshToken, config.security.jwtSecret);

      if (decoded.type !== 'refresh') {
        return res.status(401).json({
          status: 'error',
          message: 'Invalid refresh token',
        });
      }

      const user = await User.findById(decoded.sub);

      if (!user || !user.isActive) {
        return res.status(401).json({
          status: 'error',
          message: 'User not found or inactive',
        });
      }

      const accessToken = generateToken(user);

      res.json({
        status: 'success',
        data: {
          accessToken,
        },
      });
    } catch (error) {
      return res.status(401).json({
        status: 'error',
        message: 'Invalid or expired refresh token',
      });
    }
  })
);

module.exports = router;
