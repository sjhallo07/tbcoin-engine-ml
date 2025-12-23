
export default async function handler(req, res) {
  const { owner, repo } = req.query
  if (!owner || !repo) {
    res.status(400).json({ error: 'owner and repo query params are required' })
    return
  }

  const GITHUB_TOKEN = process.env.GITHUB_TOKEN || null
  const headers = {
    Accept: 'application/vnd.github+json',
    ...(GITHUB_TOKEN ? { Authorization: `Bearer ${GITHUB_TOKEN}` } : {}),
    'User-Agent': 'tbcoin-dashboard'
  }

  try {
    const url = `https://api.github.com/repos/${owner}/${repo}/actions/runs?per_page=100`
    const r = await fetch(url, { headers })
    if (!r.ok) {
      const txt = await r.text()
      return res.status(r.status).send(txt)
    }
    const json = await r.json()
    const runs = Array.isArray(json.workflow_runs) ? json.workflow_runs : json.data || []

    const total_runs = runs.length
    const completed = runs.filter(x => x.status === 'completed')
    const completed_runs = completed.length
    let success_count = 0
    let failure_count = 0
    let total_duration = 0
    const sample_runs = []

    for (const run of completed.slice(0, 10)) {
      const created = run.created_at ? new Date(run.created_at) : null
      const updated = run.updated_at ? new Date(run.updated_at) : null
      let duration_seconds = null
      if (created && updated) {
        duration_seconds = (updated.getTime() - created.getTime()) / 1000
        total_duration += duration_seconds
      }

      if (run.conclusion === 'success') success_count++
      else if (['failure', 'cancelled', 'timed_out', 'action_required'].includes(run.conclusion)) failure_count++

      sample_runs.push({
        id: run.id,
        name: run.name,
        workflow_name: run.name || run.head_branch,
        status: run.status,
        conclusion: run.conclusion,
        created_at: run.created_at,
        updated_at: run.updated_at,
        duration_seconds
      })
    }

    const avg_duration_seconds = completed_runs > 0 ? (total_duration / Math.min(completed_runs, 10)) : null
    const success_rate = completed_runs > 0 ? (success_count / completed_runs) : 0

    // As an approximate "test pass rate", use success_rate (GitHub doesn't expose a unified test pass metric via workflow runs)
    const test_pass_rate = success_rate

    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=120')
    return res.json({ owner, repo, total_runs, completed_runs, success_count, failure_count, success_rate, avg_duration_seconds, test_pass_rate, sample_runs })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: String(err) })
  }
}
