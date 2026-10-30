<script setup>
defineProps({ name: { type: String, default: 'arrow' } })
</script>

<template>
  <svg viewBox="0 0 48 48" fill="none" aria-hidden="true" class="editorial-icon">
    <path v-if="name === 'arrow'" d="M8 24h30m-11-11 11 11-11 11" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" />
    <g v-else-if="name === 'report'" fill="currentColor">
      <path d="M8 5h25v5H13v29h20v5H8zM18 15h17v3H18zm0 7h12v3H18z" />
      <circle cx="34" cy="30" r="5" /><path d="M25 44v-4a9 9 0 0 1 18 0v4z" />
    </g>
    <g v-else-if="name === 'medal'" fill="currentColor">
      <path d="m24 3 7 4 8 1 2 8 4 8-4 7-2 8-8 2-7 4-7-4-8-2-2-8-4-7 4-8 2-8 8-1z" />
      <path d="m24 12 3.5 7 8 1-5.7 5.5 1.3 8L24 30l-7.1 3.5 1.3-8-5.7-5.5 8-1z" fill="var(--vp-c-bg)" />
    </g>
    <g v-else-if="name === 'compass'" stroke="currentColor" stroke-width="3">
      <circle cx="24" cy="25" r="18" /><path d="M19 5h10M24 3v5" />
      <path d="m31 17-4 12-12 4 4-12z" fill="currentColor" stroke-linejoin="round" />
    </g>
    <g v-else-if="name === 'chart'" fill="currentColor"><path d="M5 29h7v15H5zm11-10h7v25h-7zM27 8h7v36h-7zm11 14h7v22h-7z" /></g>
  </svg>
</template>

<style scoped>
.editorial-icon { width: 1.4em; height: 1.4em; flex-shrink: 0; }
</style>
