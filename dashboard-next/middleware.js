/**
 * Next.js Middleware for Security, Validation, and Rate Limiting
 * Runs on all API routes to provide consistent security and validation
 */

import { NextResponse } from 'next/server'

// Rate limiting storage (in-memory for development)
const rateLimitMap = new Map()

// Configuration
const RATE_LIMIT_WINDOW = 60 * 1000 // 1 minute
const MAX_REQUESTS_PER_WINDOW = 60 // 60 requests per minute
const ALLOWED_ORIGINS = [
  'http://localhost:3000',
  'http://localhost:3001',
  'https://tbcoin.com',
  'https://app.tbcoin.com'
]

/**
 * Rate limiting function
 */
function checkRateLimit(identifier) {
  const now = Date.now()
  const userRequests = rateLimitMap.get(identifier) || []
  
  // Filter out old requests outside the window
  const recentRequests = userRequests.filter(
    timestamp => now - timestamp < RATE_LIMIT_WINDOW
  )
  
  if (recentRequests.length >= MAX_REQUESTS_PER_WINDOW) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: recentRequests[0] + RATE_LIMIT_WINDOW
    }
  }
  
  // Add current request
  recentRequests.push(now)
  rateLimitMap.set(identifier, recentRequests)
  
  return {
    allowed: true,
    remaining: MAX_REQUESTS_PER_WINDOW - recentRequests.length,
    resetAt: now + RATE_LIMIT_WINDOW
  }
}

/**
 * Get client identifier for rate limiting
 */
function getClientIdentifier(request) {
  // Try API key first
  const apiKey = request.headers.get('x-api-key')
  if (apiKey) return `api:${apiKey}`
  
  // Fall back to IP address
  const forwarded = request.headers.get('x-forwarded-for')
  const ip = forwarded ? forwarded.split(',')[0] : request.ip
  return `ip:${ip || 'unknown'}`
}

/**
 * Add security headers to response
 */
function addSecurityHeaders(response) {
  const headers = new Headers(response.headers)
  
  // Security headers
  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('X-Frame-Options', 'DENY')
  headers.set('X-XSS-Protection', '1; mode=block')
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
  
  // HSTS (only in production with HTTPS)
  if (process.env.NODE_ENV === 'production') {
    headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  }
  
  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  })
}

/**
 * Validate request data
 */
function validateRequest(request) {
  const contentType = request.headers.get('content-type')
  
  // For POST/PUT requests, validate content type
  if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
    if (!contentType || !contentType.includes('application/json')) {
      return {
        valid: false,
        error: 'Content-Type must be application/json'
      }
    }
  }
  
  return { valid: true }
}

/**
 * Log request for monitoring
 */
function logRequest(request) {
  const timestamp = new Date().toISOString()
  const method = request.method
  const url = request.url
  const userAgent = request.headers.get('user-agent') || 'unknown'
  
  console.log(`[${timestamp}] ${method} ${url} - UA: ${userAgent}`)
}

/**
 * Main middleware function
 */
export function middleware(request) {
  // Skip middleware for static files and internal routes
  if (
    request.nextUrl.pathname.startsWith('/_next') ||
    request.nextUrl.pathname.startsWith('/static') ||
    request.nextUrl.pathname === '/favicon.ico'
  ) {
    return NextResponse.next()
  }
  
  // Log request
  logRequest(request)
  
  // Check rate limit for API routes
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const identifier = getClientIdentifier(request)
    const rateLimitCheck = checkRateLimit(identifier)
    
    if (!rateLimitCheck.allowed) {
      return new NextResponse(
        JSON.stringify({
          error: 'Rate limit exceeded',
          message: 'Too many requests. Please try again later.',
          retryAfter: Math.ceil((rateLimitCheck.resetAt - Date.now()) / 1000)
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': String(Math.ceil((rateLimitCheck.resetAt - Date.now()) / 1000)),
            'X-RateLimit-Limit': String(MAX_REQUESTS_PER_WINDOW),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': String(rateLimitCheck.resetAt)
          }
        }
      )
    }
    
    // Validate request
    const validation = validateRequest(request)
    if (!validation.valid) {
      return new NextResponse(
        JSON.stringify({
          error: 'Invalid request',
          message: validation.error
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }
    
    // Add rate limit headers to response
    const response = NextResponse.next()
    response.headers.set('X-RateLimit-Limit', String(MAX_REQUESTS_PER_WINDOW))
    response.headers.set('X-RateLimit-Remaining', String(rateLimitCheck.remaining))
    response.headers.set('X-RateLimit-Reset', String(rateLimitCheck.resetAt))
    
    return addSecurityHeaders(response)
  }
  
  // For non-API routes, just add security headers
  return addSecurityHeaders(NextResponse.next())
}

// Configure which routes the middleware runs on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}
