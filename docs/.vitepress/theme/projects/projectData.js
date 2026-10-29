let pending

export function loadProjectStats() {
  if (!pending) {
    const base = (import.meta.env.BASE_URL || '/').replace(/\/+$/, '')
    pending = fetch(`${base}/data/datawhalechina/organization_datasource.json`)
      .then(response => {
        if (!response.ok) throw new Error(`数据请求失败（${response.status}）`)
        return response.json()
      })
      .catch(error => { pending = null; throw error })
  }
  return pending
}

export function sortedMonths(items) {
  return [...new Set(items.flatMap(item => Object.keys(item.monthly_total_stars || {})))]
    .sort((a, b) => {
      const [ay, am] = a.split('-').map(Number)
      const [by, bm] = b.split('-').map(Number)
      return ay - by || am - bm
    })
}

export function formatStars(value) {
  const absolute = Math.abs(value)
  if (absolute >= 10000) return `${Number((value / 10000).toFixed(1))}万`
  if (absolute >= 1000) return `${Number((value / 1000).toFixed(1))}千`
  return String(value)
}
