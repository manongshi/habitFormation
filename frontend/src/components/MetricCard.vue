<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  tone: { type: String, default: 'blue' },
})
</script>

<template>
  <article class="metric-card" :class="`metric-card--${tone}`">
    <span class="metric-card__label">{{ label }}</span>
    <p class="metric-card__value">{{ value }}<small>{{ unit }}</small></p>
  </article>
</template>

