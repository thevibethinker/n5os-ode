import { useEffect, useState } from 'react'

export default function Feed() {
  const [lines, setLines] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  async function fetchAudit() {
    try {
      const res = await fetch('/api/zobridge/audit?tail=200')
      if (!res.ok) throw new Error('Failed to load audit')
      const data = await res.json()
      setLines(data.lines || [])
    } catch (e: any) {
      setError(e.message)
    }
  }

  useEffect(() => {
    fetchAudit()
    const id = setInterval(fetchAudit, 2000)
    return () => clearInterval(id)
  }, [])

  return (
    <div style={{ fontFamily: 'monospace', padding: 16 }}>
      <h2>ZoBridge Feed</h2>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <pre style={{ whiteSpace: 'pre-wrap' }}>{lines.join('\n')}</pre>
    </div>
  )
}
