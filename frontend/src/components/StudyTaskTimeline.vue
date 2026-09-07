<script setup>
defineProps({
  tasks: { type: Array, required: true },
  tone: { type: String, default: 'light' },
  checkable: { type: Boolean, default: false },
  updatingTaskId: { type: Number, default: null },
})

defineEmits(['toggle'])

function formatTime(value) {
  return value?.slice(0, 5)
}
</script>

<template>
  <div class="study-task-timeline" :class="`is-${tone}`">
    <div v-for="task in tasks" :key="task.id" class="timeline-task" :class="{ 'is-break': task.is_break, completed: task.status === 'completed' }">
      <time>{{ formatTime(task.scheduled_start) }}<template v-if="tone === 'light'">–{{ formatTime(task.scheduled_end) }}</template></time>
      <button
        v-if="checkable && !task.is_break"
        type="button"
        class="task-checkbox"
        :class="{ checked: task.status === 'completed' }"
        :disabled="updatingTaskId === task.id"
        :aria-label="task.status === 'completed' ? `取消完成${task.title}` : `完成${task.title}`"
        @click="$emit('toggle', task)"
      ><span class="task-checkbox__mark" aria-hidden="true"></span></button>
      <i v-else aria-hidden="true"></i>
      <div>
        <strong>{{ task.title }}</strong>
        <span>{{ task.description }}</span>
      </div>
      <small>{{ task.duration_minutes }} 分钟</small>
    </div>
  </div>
</template>

<style scoped>
.study-task-timeline{--track:#cfd9e3;--dot:#3157d5;--time:#61738a;--title:#17233c;--copy:#8290a1}.timeline-task{min-height:48px;display:grid;grid-template-columns:92px 16px 1fr auto;gap:10px;align-items:start;position:relative}.timeline-task>time{padding-top:2px;color:var(--time);font:700 10px "SFMono-Regular",monospace}.timeline-task>i,.task-checkbox{width:9px;height:9px;margin-top:3px;position:relative;z-index:1;border:0;border-radius:50%;background:var(--dot)}.timeline-task:not(:last-child)>i:after,.timeline-task:not(:last-child)>.task-checkbox:after{content:"";width:1px;height:39px;position:absolute;top:13px;left:6px;background:var(--track)}.task-checkbox{width:14px;height:14px;margin-top:0;padding:0;display:grid;place-items:center;border:1.5px solid #aebbc9;background:#f8fbfe;box-shadow:0 0 0 3px #f2f6fa;cursor:pointer;transition:border-color .16s ease,background-color .16s ease,box-shadow .16s ease,transform .16s ease}.task-checkbox:hover{border-color:#3157d5;box-shadow:0 0 0 3px rgb(49 87 213/10%);transform:scale(1.08)}.task-checkbox.checked{border-color:#3157d5;background:#3157d5;box-shadow:0 0 0 3px rgb(49 87 213/12%)}.task-checkbox__mark{width:4px;height:7px;margin-top:-1px;border-right:1.5px solid #fff;border-bottom:1.5px solid #fff;opacity:0;transform:rotate(45deg) scale(.7);transition:opacity .14s ease,transform .14s ease}.task-checkbox.checked .task-checkbox__mark{opacity:1;transform:rotate(45deg) scale(1)}.task-checkbox:disabled{cursor:wait;opacity:.55}.task-checkbox:focus-visible{outline:3px solid rgb(49 87 213/24%);outline-offset:3px}.timeline-task>div{display:grid;gap:2px}.timeline-task>div strong{color:var(--title);font-size:11px}.timeline-task>div span{color:var(--copy);font-size:9px;line-height:1.5}.timeline-task>small{padding-top:2px;color:var(--copy);font-size:9px}.timeline-task.is-break>i{background:#51a77c}.timeline-task.is-break>div strong{color:#318260}.timeline-task.completed>div strong{color:#76869a;text-decoration:line-through;text-decoration-color:#a9b5c3;text-decoration-thickness:1px}.timeline-task.completed>div span{opacity:.62}.study-task-timeline.is-dark{--track:rgb(255 255 255/16%);--dot:#9eb2ff;--time:#aebbd0;--title:#fff;--copy:#9eacbf}.is-dark .timeline-task{min-height:54px;grid-template-columns:46px 14px 1fr auto}.is-dark .timeline-task>i{width:8px;height:8px;border:2px solid var(--dot);background:#17233c}.is-dark .timeline-task:not(:last-child)>i:after{height:48px;left:2px}.is-dark .timeline-task.is-break>i{border-color:#62bc91}.is-dark .timeline-task.is-break>div strong{color:#82d2aa}@media(max-width:680px){.timeline-task{grid-template-columns:78px 16px 1fr}.timeline-task>small{display:none}.is-dark .timeline-task{grid-template-columns:42px 12px 1fr}}@media(prefers-reduced-motion:reduce){.task-checkbox,.task-checkbox__mark{transition:none}}
</style>
