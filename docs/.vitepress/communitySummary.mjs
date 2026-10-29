import { readFileSync, existsSync } from 'node:fs'

// Only the summary is shipped to the homepage; the full datasets stay out of its JS.
export function communitySummary() {
  const read = (name, fallback) => {
    const source = new URL(`../public/data/${name}`, import.meta.url)
    return existsSync(source) ? JSON.parse(readFileSync(source, 'utf8')) : fallback
  }
  const members = read('members.json', null)
  const repositories = read('datawhalechina/organization/repo_list.json', null)
  const weekly = read('commits_weekly.json', {})
  const periods = read('datawhalechina/fetch_time_key.json', [])
  const domains = new Set((members || []).flatMap(member =>
    String(member.domain || '').split(';').map(value => value.trim()).filter(Boolean)))
  return {
    contributors: members?.length ?? null,
    repositories: repositories?.length ?? null,
    domains: members ? domains.size : null,
    commits: weekly.total_commits ?? null,
    days: weekly.days_range ?? null,
    updated: weekly.update_time?.slice(0, 10) || '',
    projectPeriod: periods.at(-1) || ''
  }
}
