<script setup>
defineProps({
  tasks: { type: Array, required: true },
})
</script>

<template>
  <div class="task-timeline">
    <article v-for="(task, index) in tasks" :key="task.title" class="task-item">
      <div class="task-item__track">
        <span>{{ index + 1 }}</span>
      </div>
      <div class="task-item__content">
        <div>
          <strong>{{ task.title }}</strong>
          <p>{{ task.description }}</p>
        </div>
        <span class="task-item__time">{{ task.minutes }} 分钟</span>
      </div>
    </article>
  </div>
</template>

