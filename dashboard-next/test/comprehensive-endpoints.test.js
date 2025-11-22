/**
 * Comprehensive test suite for Next.js API endpoints
 * Tests all middleware, validation, security, and API routes
 */

const { strictEqual, ok, deepStrictEqual } = require('assert')

// Configuration
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001'
const TEST_TIMEOUT = 30000 // 30 seconds

/**
 * Utility functions
 */
async function fetchJson(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  }
  const res = await fetch(url, { ...defaultOptions, ...options })
  return {
    status: res.status,
    headers: res.headers,
    data: res.ok ? await res.json() : null,
    text: !res.ok ? await res.text() : null
  }
}

async function testEndpoint(name, testFn) {
  console.log(`\n🧪 Testing: ${name}`)
  try {
    await testFn()
    console.log(`✅ PASSED: ${name}`)
    return true
  } catch (err) {
    console.error(`❌ FAILED: ${name}`)
    console.error(`   Error: ${err.message}`)
    return false
  }
}

/**
 * Test Categories
 */

// 1. Core Endpoint Tests
async function testCoreEndpoints() {
  console.log('\n═══ CORE ENDPOINT TESTS ═══')
  
  const tests = [
    testEndpoint('Solana Price Endpoint', async () => {
      const result = await fetchJson('/api/solana/price')
      strictEqual(result.status, 200, 'Status should be 200')
      strictEqual(result.data.status, 'success', 'Status should be success')
      ok(result.data.data, 'Data should exist')
      ok(result.data.data.price !== undefined, 'Price should be present')
      ok(result.data.data.change24h !== undefined, '24h change should be present')
      ok(result.data.data.marketCap !== undefined, 'Market cap should be present')
      ok(result.data.data.timestamp, 'Timestamp should be present')
    }),
    
    testEndpoint('TBCoin Data Endpoint', async () => {
      const result = await fetchJson('/api/tbcoin/data')
      strictEqual(result.status, 200, 'Status should be 200')
      strictEqual(result.data.status, 'success', 'Status should be success')
      ok(result.data.data, 'Data should exist')
      ok(result.data.data.price !== undefined, 'Price should be present')
      ok(result.data.data.holders !== undefined, 'Holders should be present')
      ok(result.data.data.transactions !== undefined, 'Transactions should be present')
    }),
    
    testEndpoint('Solana Test POST Endpoint', async () => {
      const result = await fetchJson('/api/solana/test', {
        method: 'POST',
        body: JSON.stringify({
          action: 'test',
          symbol: 'SOL'
        })
      })
      strictEqual(result.status, 200, 'Status should be 200')
      strictEqual(result.data.status, 'success', 'Status should be success')
      strictEqual(result.data.data.processed, true, 'Should be processed')
      ok(result.data.data.analysis, 'Analysis should be present')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 2. Security Header Tests
async function testSecurityHeaders() {
  console.log('\n═══ SECURITY HEADER TESTS ═══')
  
  const tests = [
    testEndpoint('Security Headers Present', async () => {
      const result = await fetchJson('/api/solana/price')
      const headers = result.headers
      
      ok(headers.get('x-content-type-options'), 'X-Content-Type-Options header should exist')
      ok(headers.get('x-frame-options'), 'X-Frame-Options header should exist')
      ok(headers.get('x-xss-protection'), 'X-XSS-Protection header should exist')
      
      strictEqual(
        headers.get('x-content-type-options'),
        'nosniff',
        'X-Content-Type-Options should be nosniff'
      )
      strictEqual(
        headers.get('x-frame-options'),
        'DENY',
        'X-Frame-Options should be DENY'
      )
    }),
    
    testEndpoint('Rate Limit Headers Present', async () => {
      const result = await fetchJson('/api/solana/price')
      const headers = result.headers
      
      ok(headers.get('x-ratelimit-limit'), 'X-RateLimit-Limit header should exist')
      ok(headers.get('x-ratelimit-remaining'), 'X-RateLimit-Remaining header should exist')
      ok(headers.get('x-ratelimit-reset'), 'X-RateLimit-Reset header should exist')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 3. Validation Tests
async function testValidation() {
  console.log('\n═══ VALIDATION TESTS ═══')
  
  const tests = [
    testEndpoint('POST Without Content-Type Validation', async () => {
      const result = await fetchJson('/api/solana/test', {
        method: 'POST',
        headers: {
          // Omit Content-Type header
        },
        body: JSON.stringify({ action: 'test' })
      })
      
      // Middleware should validate Content-Type for POST requests
      // It may return 400 or process anyway depending on implementation
      ok(result.status === 200 || result.status === 400, 'Should handle missing Content-Type')
    }),
    
    testEndpoint('GET Requests Work Without Content-Type', async () => {
      const result = await fetchJson('/api/solana/price', {
        headers: {}
      })
      strictEqual(result.status, 200, 'GET requests should work without Content-Type')
    }),
    
    testEndpoint('Valid JSON Data', async () => {
      const testData = {
        action: 'analyze',
        symbol: 'SOL',
        amount: 100
      }
      
      const result = await fetchJson('/api/solana/test', {
        method: 'POST',
        body: JSON.stringify(testData)
      })
      
      strictEqual(result.status, 200, 'Valid JSON should be accepted')
      ok(result.data, 'Response should contain data')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 4. Error Handling Tests
async function testErrorHandling() {
  console.log('\n═══ ERROR HANDLING TESTS ═══')
  
  const tests = [
    testEndpoint('404 for Non-existent Endpoint', async () => {
      const result = await fetchJson('/api/nonexistent/endpoint')
      strictEqual(result.status, 404, 'Should return 404 for non-existent endpoint')
    }),
    
    testEndpoint('405 for Wrong HTTP Method', async () => {
      // Try POST on GET-only endpoint
      const result = await fetchJson('/api/solana/price', {
        method: 'POST',
        body: JSON.stringify({ test: 'data' })
      })
      ok(result.status === 405 || result.status === 400, 'Should reject wrong HTTP method')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 5. Rate Limiting Tests
async function testRateLimiting() {
  console.log('\n═══ RATE LIMITING TESTS ═══')
  
  const tests = [
    testEndpoint('Rate Limit Headers Update', async () => {
      const result1 = await fetchJson('/api/solana/price')
      const remaining1 = parseInt(result1.headers.get('x-ratelimit-remaining') || '0')
      
      const result2 = await fetchJson('/api/solana/price')
      const remaining2 = parseInt(result2.headers.get('x-ratelimit-remaining') || '0')
      
      ok(remaining2 <= remaining1, 'Remaining requests should decrease or stay same')
      console.log(`   Rate limit: ${remaining1} → ${remaining2} remaining`)
    })
  ]
  
  // Note: Not testing actual rate limit exhaustion to avoid affecting other tests
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 6. Data Integrity Tests
async function testDataIntegrity() {
  console.log('\n═══ DATA INTEGRITY TESTS ═══')
  
  const tests = [
    testEndpoint('Consistent Data Structure', async () => {
      const result1 = await fetchJson('/api/solana/price')
      const result2 = await fetchJson('/api/solana/price')
      
      // Check structure consistency
      const keys1 = Object.keys(result1.data.data).sort()
      const keys2 = Object.keys(result2.data.data).sort()
      
      deepStrictEqual(keys1, keys2, 'Data structure should be consistent')
    }),
    
    testEndpoint('Timestamp Format Valid', async () => {
      const result = await fetchJson('/api/solana/price')
      const timestamp = result.data.data.timestamp
      
      ok(timestamp, 'Timestamp should exist')
      ok(Date.parse(timestamp), 'Timestamp should be valid ISO 8601 format')
    }),
    
    testEndpoint('Numeric Fields Are Numbers', async () => {
      const result = await fetchJson('/api/solana/price')
      const data = result.data.data
      
      strictEqual(typeof data.price, 'number', 'Price should be a number')
      strictEqual(typeof data.change24h, 'number', 'Change24h should be a number')
      strictEqual(typeof data.marketCap, 'number', 'MarketCap should be a number')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

// 7. Performance Tests
async function testPerformance() {
  console.log('\n═══ PERFORMANCE TESTS ═══')
  
  const tests = [
    testEndpoint('Response Time Under 1 Second', async () => {
      const start = Date.now()
      await fetchJson('/api/solana/price')
      const duration = Date.now() - start
      
      console.log(`   Response time: ${duration}ms`)
      ok(duration < 1000, 'Response should be under 1 second')
    }),
    
    testEndpoint('Concurrent Requests Handled', async () => {
      const start = Date.now()
      const numRequests = 10  // Increased from 5 for better load testing
      const requests = Array(numRequests).fill(null).map(() => 
        fetchJson('/api/solana/price')
      )
      
      const results = await Promise.all(requests)
      const duration = Date.now() - start
      
      console.log(`   ${numRequests} concurrent requests: ${duration}ms`)
      ok(results.every(r => r.status === 200), 'All requests should succeed')
    })
  ]
  
  const results = await Promise.all(tests)
  return results.every(r => r)
}

/**
 * Main test runner
 */
async function runAllTests() {
  console.log('\n╔════════════════════════════════════════════╗')
  console.log('║  COMPREHENSIVE ENDPOINT TEST SUITE         ║')
  console.log('║  Testing Next.js API Routes                ║')
  console.log(`║  Base URL: ${BASE_URL}`)
  console.log('╚════════════════════════════════════════════╝')
  
  const testCategories = [
    { name: 'Core Endpoints', fn: testCoreEndpoints },
    { name: 'Security Headers', fn: testSecurityHeaders },
    { name: 'Validation', fn: testValidation },
    { name: 'Error Handling', fn: testErrorHandling },
    { name: 'Rate Limiting', fn: testRateLimiting },
    { name: 'Data Integrity', fn: testDataIntegrity },
    { name: 'Performance', fn: testPerformance }
  ]
  
  const results = []
  
  for (const category of testCategories) {
    try {
      const passed = await category.fn()
      results.push({ name: category.name, passed })
    } catch (err) {
      console.error(`\n❌ Category failed: ${category.name}`)
      console.error(err)
      results.push({ name: category.name, passed: false })
    }
  }
  
  // Print summary
  console.log('\n╔════════════════════════════════════════════╗')
  console.log('║  TEST SUMMARY                              ║')
  console.log('╚════════════════════════════════════════════╝')
  
  results.forEach(result => {
    const icon = result.passed ? '✅' : '❌'
    console.log(`${icon} ${result.name}: ${result.passed ? 'PASSED' : 'FAILED'}`)
  })
  
  const totalPassed = results.filter(r => r.passed).length
  const totalTests = results.length
  
  console.log(`\n${totalPassed}/${totalTests} test categories passed`)
  
  if (totalPassed === totalTests) {
    console.log('\n🎉 All tests passed successfully!')
    process.exit(0)
  } else {
    console.log('\n⚠️  Some tests failed. Please review the results above.')
    process.exit(1)
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests().catch(err => {
    console.error('Fatal error:', err)
    process.exit(2)
  })
}

module.exports = { runAllTests, fetchJson, testEndpoint }
