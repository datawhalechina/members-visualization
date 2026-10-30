// Read the shared page tokens when a chart renders, including after theme changes.
export function getChartTheme(dark = false) {
  const style = typeof document === 'undefined' ? null : getComputedStyle(document.documentElement)
  const token = (name, fallback) => style?.getPropertyValue(name).trim() || fallback
  return {
    text: token('--vp-c-text-2', dark ? '#b6bcaf' : '#626760'),
    ink: token('--vp-c-text-1', dark ? '#eee9dc' : '#172629'),
    paper: token('--vp-c-bg', dark ? '#202724' : '#f6f3eb'),
    soft: token('--vp-c-bg-soft', dark ? '#2a322d' : '#eeebe2'),
    rule: token('--vp-c-divider', dark ? '#4b574d' : '#c6c7bb'),
    font: token('--vp-font-family-base', 'sans-serif'),
    palette: dark
      ? ['#8eb4ed', '#ed876f', '#8bb7a9', '#d7b770', '#abb5c1', '#a8c5db', '#97ae7b', '#c7a5b8']
      : ['#2765bd', '#de513c', '#538d80', '#b58d42', '#6b7c8c', '#79a5c8', '#71864d', '#9a6e86']
  }
}
