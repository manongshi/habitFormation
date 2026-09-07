<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
})
</script>

<template>
  <section class="placeholder-page">
    <span class="eyebrow">功能准备中</span>
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
  </section>
</template>
