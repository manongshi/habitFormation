<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useUserStore } from '../store/userStore'
import { sendEmailCode } from '../services/api'

const props = defineProps({
  mode: { type: String, required: true },
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ nickname: '', email: '', email_code: '', password: '' })
const isRegister = computed(() => props.mode === 'register')
const codeSending = ref(false)
const countdown = ref(0)
let countdownTimer

async function requestEmailCode() {
  if (!form.email) {
    errorMessage.value = '请先填写邮箱'
    return
  }
  codeSending.value = true
  errorMessage.value = ''
  try {
    const result = await sendEmailCode(form.email)
    countdown.value = result.cooldown
    countdownTimer = window.setInterval(() => {
      countdown.value -= 1
      if (countdown.value <= 0) {
        window.clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    codeSending.value = false
  }
}

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    if (isRegister.value) {
      await userStore.register(form)
      router.replace('/certificates')
    } else {
      await userStore.login({ email: form.email, password: form.password })
      router.replace(route.query.redirect || '/')
    }
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    submitting.value = false
  }
}

onBeforeUnmount(() => window.clearInterval(countdownTimer))
</script>

<template>
  <main class="auth-page">
    <section class="auth-story">
      <RouterLink class="brand" to="/">
        <span class="brand__mark">准</span>
        <span>AI 考证教练</span>
      </RouterLink>
      <div>
        <span class="eyebrow">练习不是终点</span>
        <h1>每一次答错，<br />都应该带你更接近掌握。</h1>
        <p>AI 教练会记住你的考试目标、错误原因与遗忘节奏，持续安排真正需要的下一题。</p>
      </div>
      <div class="auth-loop" aria-label="学习闭环">
        <span>练习</span><i>→</i><span>诊断</span><i>→</i><span>讲解</span><i>→</i><span>复测</span>
      </div>
    </section>

    <section class="auth-panel">
      <form class="auth-form" @submit.prevent="submit">
        <span class="eyebrow">{{ isRegister ? '创建学习档案' : '继续今天的训练' }}</span>
        <h2>{{ isRegister ? '注册账号' : '欢迎回来' }}</h2>
        <p>{{ isRegister ? '用一个账号保存你的掌握轨迹。' : '登录后从上次的薄弱点继续。' }}</p>

        <label v-if="isRegister">
          怎么称呼你
          <input v-model.trim="form.nickname" required minlength="2" maxlength="60" placeholder="你的昵称" autocomplete="nickname" />
        </label>
        <label>
          邮箱
          <input v-model.trim="form.email" required type="email" placeholder="name@example.com" autocomplete="email" />
        </label>
        <label v-if="isRegister">
          邮箱验证码
          <div class="verification-input">
            <input
              v-model.trim="form.email_code"
              required
              inputmode="numeric"
              maxlength="6"
              pattern="\d{6}"
              placeholder="6 位验证码"
              autocomplete="one-time-code"
            />
            <button
              type="button"
              :disabled="codeSending || countdown > 0"
              @click="requestEmailCode"
            >
              {{ countdown > 0 ? `${countdown} 秒` : codeSending ? '发送中…' : '获取验证码' }}
            </button>
          </div>
        </label>
        <label>
          密码
          <input v-model="form.password" required type="password" minlength="8" maxlength="72" placeholder="至少 8 位" :autocomplete="isRegister ? 'new-password' : 'current-password'" />
        </label>

        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <button class="primary-button primary-button--wide" type="submit" :disabled="submitting">
          {{ submitting ? '请稍候…' : isRegister ? '注册并开始' : '登录' }}
        </button>

        <p class="auth-switch">
          {{ isRegister ? '已经有账号？' : '还没有账号？' }}
          <RouterLink :to="isRegister ? '/login' : '/register'">
            {{ isRegister ? '直接登录' : '免费注册' }}
          </RouterLink>
        </p>
      </form>
    </section>
  </main>
</template>
