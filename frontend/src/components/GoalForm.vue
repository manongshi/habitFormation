<script setup>
import { reactive, ref } from 'vue'

import { createExamGoal } from '../services/api'

const emit = defineEmits(['created', 'cancel'])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  exam_name: '',
  exam_date: '',
  target_score: 60,
  daily_minutes: 60,
  current_level: '',
})

async function submitGoal() {
  submitting.value = true
  errorMessage.value = ''
  try {
    const goal = await createExamGoal(form)
    emit('created', goal)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="goal-form" @submit.prevent="submitGoal">
    <div class="form-heading">
      <div>
        <span class="eyebrow">建立目标</span>
        <h2>先告诉教练终点在哪里</h2>
      </div>
      <button class="icon-button" type="button" aria-label="关闭" @click="$emit('cancel')">×</button>
    </div>

    <label>
      考试名称
      <input v-model.trim="form.exam_name" required minlength="2" placeholder="例如：教师资格证笔试" />
    </label>

    <div class="form-grid">
      <label>
        考试日期
        <input v-model="form.exam_date" required type="date" />
      </label>
      <label>
        目标分数
        <input v-model.number="form.target_score" required type="number" min="1" max="1000" />
      </label>
    </div>

    <div class="form-grid">
      <label>
        每日学习时间
        <div class="input-unit">
          <input v-model.number="form.daily_minutes" required type="number" min="10" max="720" />
          <span>分钟</span>
        </div>
      </label>
      <label>
        当前水平
        <input v-model.trim="form.current_level" placeholder="例如：刚开始准备" />
      </label>
    </div>

    <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>

    <button class="primary-button primary-button--wide" type="submit" :disabled="submitting">
      {{ submitting ? '正在创建…' : '生成备考起点' }}
    </button>
  </form>
</template>

