const assert = require('assert')

async function fetchJson(path) {
  const url = `http://localhost:3001${path}`
  const res = await fetch(url, { method: 'GET' })
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`)
  return res.json()
}

async function testPost(path, body) {
  const url = `http://localhost:3001${path}`
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`)
  return res.json()
}

async function main() {
  console.log('Running endpoint tests against http://localhost:3001 ...')
  try {
    const sol = await fetchJson('/api/solana/price')
    assert.strictEqual(sol.status, 'success', 'solana status')
    assert.ok(sol.data.price !== undefined, 'sol price present')

    const tb = await fetchJson('/api/tbcoin/data')
    assert.strictEqual(tb.status, 'success', 'tbcoin status')
    assert.ok(tb.data.holders !== undefined, 'tbcoin holders present')

    const post = await testPost('/api/solana/test', { action: 'test', symbol: 'SOL' })
    assert.strictEqual(post.status, 'success', 'post status')
    assert.strictEqual(post.data.processed, true, 'post processed')

    console.log('All endpoint tests passed ✅')
    process.exit(0)
  } catch (err) {
    console.error('Endpoint test failed:', err)
    process.exit(2)
  }
}

main()
