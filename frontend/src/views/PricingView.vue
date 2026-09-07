<script setup>
import { onMounted, ref } from 'vue'

import { createPaymentOrder, getPlans, getSubscription, mockPayOrder } from '../services/api'

const plans = ref([])
const subscription = ref(null)
const loading = ref(true)
const payingCode = ref('')
const message = ref('')
const errorMessage = ref('')

function formatPrice(cents) {
  return `¥${(cents / 100).toFixed(0)}`
}

async function loadPricing() {
  loading.value = true
  try {
    const [planData, subscriptionData] = await Promise.all([getPlans(), getSubscription()])
    plans.value = planData
    subscription.value = subscriptionData
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function choosePlan(plan) {
  payingCode.value = plan.code
  message.value = ''
  errorMessage.value = ''
  try {
    const order = await createPaymentOrder(plan.code)
    const result = await mockPayOrder(order.order_no)
    subscription.value = result.subscription
    message.value = `支付完成，${result.subscription.plan_name} 已生效。`
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    payingCode.value = ''
  }
}

onMounted(loadPricing)
</script>

<template>
  <div class="pricing-page">
    <div class="pricing-main">
      <div class="pricing-heading">
        <span class="eyebrow">选择教练周期</span>
        <h1>把每一次练习，变成可验证的进步</h1>
        <p>所有付费套餐均包含错因诊断、针对性讲解、变式复测与掌握地图。</p>
      </div>

      <div v-if="subscription" class="subscription-banner">
        <div>
          <span>当前套餐</span>
          <strong>{{ subscription.plan_name }}</strong>
        </div>
        <p>有效期至 {{ new Date(subscription.expires_at).toLocaleDateString('zh-CN') }}</p>
      </div>

      <p v-if="message" class="success-notice">{{ message }}</p>
      <p v-if="errorMessage" class="connection-notice">{{ errorMessage }}</p>

      <div v-if="!loading" class="pricing-grid">
        <article v-for="plan in plans" :key="plan.code" class="plan-card" :class="{ 'plan-card--featured': plan.code === 'coach_yearly' }">
          <span v-if="plan.code === 'coach_yearly'" class="plan-card__tag">更适合长期备考</span>
          <h2>{{ plan.name }}</h2>
          <p>{{ plan.description }}</p>
          <div class="plan-card__price">
            <strong>{{ formatPrice(plan.price_cents) }}</strong>
            <span>/ {{ plan.duration_days === 365 ? '年' : '月' }}</span>
          </div>
          <ul>
            <li>按考试日期动态安排每日任务</li>
            <li>追问解题思路，定位真实错因</li>
            <li>变式题与延迟复测确认掌握</li>
            <li>完整错题记录与薄弱点地图</li>
          </ul>
          <button class="primary-button primary-button--wide" :disabled="Boolean(payingCode)" @click="choosePlan(plan)">
            {{ payingCode === plan.code ? '正在完成支付…' : '选择这个套餐' }}
          </button>
        </article>
      </div>

      <p class="payment-hint">当前为开发环境模拟支付。接入正式商户渠道后，此处将跳转至对应收银台。</p>
    </div>
  </div>
</template>
