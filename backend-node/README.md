# TB Coin Engine - Node.js Backend

This is the Node.js backend component of the TB Coin Engine, designed to work alongside the Python FastAPI backend for seamless synchronization and job execution.

## Features

- **Express.js API**: RESTful API with proper routing, middleware, and error handling
- **MongoDB Integration**: Mongoose ODM for schema management and database operations
- **Authentication**: JWT-based authentication with role-based access control (RBAC)
- **Job Queue**: Job execution service for various coin engine operations
- **Security**: Rate limiting, input validation, security headers, and XSS prevention
- **Logging**: Winston-based structured logging
- **Python Backend Sync**: Service for synchronizing with the Python FastAPI backend

## Project Structure

```
backend-node/
├── src/
│   ├── config/           # Configuration and database setup
│   │   ├── index.js      # Environment configuration
│   │   └── database.js   # MongoDB connection
│   ├── middleware/       # Express middleware
│   │   ├── auth.js       # JWT authentication & RBAC
│   │   ├── errorHandler.js
│   │   └── requestLogger.js
│   ├── models/           # Mongoose models
│   │   ├── User.js
│   │   ├── Transaction.js
│   │   └── Job.js
│   ├── routes/           # API routes
│   │   ├── auth.js
│   │   ├── health.js
│   │   └── jobs.js
│   ├── services/         # Business logic
│   │   ├── jobService.js
│   │   └── pythonBackendService.js
│   ├── utils/            # Utilities
│   │   ├── logger.js
│   │   └── validation.js
│   └── index.js          # Application entry point
└── package.json
```

## Quick Start

### Prerequisites

- Node.js 18+
- MongoDB 6+
- Python backend running (for full functionality)

### Installation

```bash
cd backend-node
npm install
```

### Environment Variables

Create a `.env` file:

```env
# Application
NODE_ENV=development
NODE_PORT=3000

# Security
JWT_SECRET_KEY=your-secret-key
API_KEY=your-api-key

# MongoDB
MONGODB_URI=mongodb://localhost:27017/tbcoin

# Python Backend
PYTHON_BACKEND_URL=http://localhost:8000
```

### Running

```bash
# Development with hot reload
npm run dev

# Production
npm start
```

## API Endpoints

### Health
- `GET /health` - Health check with service status
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token

### Jobs
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs/:jobId` - Get job by ID
- `POST /api/v1/jobs/:jobId/execute` - Execute job
- `POST /api/v1/jobs/:jobId/cancel` - Cancel job
- `GET /api/v1/jobs/status/:status` - Get jobs by status

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Role-Based Access Control**: Admin, Operator, User, Viewer roles
3. **Rate Limiting**: Configurable request limits
4. **Input Validation**: express-validator for all inputs
5. **Security Headers**: Helmet middleware
6. **XSS Prevention**: Input sanitization
7. **NoSQL Injection Prevention**: Query sanitization

## Testing

```bash
npm test
```

## Integration with Python Backend

The Node.js backend communicates with the Python FastAPI backend via HTTP:

1. **Health Checks**: Monitors Python backend status
2. **Job Execution**: Delegates ML and blockchain jobs
3. **Data Sync**: Synchronizes transaction and user data

## License

MIT
