<script setup>
import { ArrowRight, Calendar, Clock } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import StudyPlanDrawer from '../components/StudyPlanDrawer.vue'
import StudyTaskTimeline from '../components/StudyTaskTimeline.vue'
import { getStudyPlan, getStudyPlans } from '../services/api'

const router = useRouter()
const route = useRoute()
const plans = ref([])
const selectedPlan = ref(null)
const fullPlan = ref(null)
const drawerVisible = ref(false)
const loading = ref(true)
const loadingFullPlan = ref(false)
const errorMessage = ref('')

const selectedDate = computed(() => String(route.query.date || ''))
const todayLabel = computed(() => new Intl.DateTimeFormat('zh-CN', {
  month: 'long', day: 'numeric', weekday: 'long',
}).format(selectedDate.value ? new Date(`${selectedDate.value}T00:00:00`) : new Date()))
const todayMinutes = computed(() => selectedPlan.value?.today?.study_minutes || 0)
const todayTaskCount = computed(() => selectedPlan.value?.today?.tasks?.filter((task) => !task.is_break).length || 0)
const todayPlanCount = computed(() => plans.value.filter((plan) => plan.today).length)

function sourceLabel(mode) {
  return { deepseek: 'DeepSeek', qwen: 'Qwen', ai: 'AI', rules: '智能规则' }[mode] || 'AI'
}

function formatDate(value) {
  if (!value) return ''
  const [, month, day] = value.split('-')
  return `${Number(month)}月${Number(day)}日`
}

function selectPlan(plan) {
  if (selectedPlan.value?.id === plan.id) {
    openFullPlan(plan)
    return
  }
  selectedPlan.value = plan
}

async function openFullPlan(plan = selectedPlan.value) {
  if (!plan || loadingFullPlan.value) return
  loadingFullPlan.value = true
  errorMessage.value = ''
  try {
    fullPlan.value = await getStudyPlan(plan.id)
    drawerVisible.value = true
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loadingFullPlan.value = false
  }
}

async function loadPlans() {
  loading.value = true
  errorMessage.value = ''
  try {
    const previousPlanId = selectedPlan.value?.id
    plans.value = await getStudyPlans(selectedDate.value)
    const requestedPlanId = Number(route.query.plan)
    const targetPlanId = requestedPlanId || previousPlanId
    if (targetPlanId) selectedPlan.value = plans.value.find((plan) => plan.id === targetPlanId) || null
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(loadPlans)
</script>

<template>
  <div class="today-page">
    <section class="today-hero">
      <div>
        <span class="today-kicker">今日训练台 · {{ todayLabel }}</span>
        <h2>今天，只完成计划里的这一小段。</h2>
        <p>选择一张正在准备的证书，查看 AI 为今天安排的学习与休息。</p>
      </div>
      <div class="hero-ledger">
        <strong>{{ todayPlanCount }}</strong>
        <span>个计划今天有任务</span>
      </div>
    </section>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

    <section v-loading="loading" class="training-workspace">
      <aside class="plan-index">
        <div class="index-heading">
          <div><span>MY PLANS</span><h3>我的备考列表</h3></div>
          <small>再次点击可看全部</small>
        </div>

        <div v-if="plans.length" class="plan-list">
          <button
            v-for="plan in plans"
            :key="plan.id"
            type="button"
            class="plan-row"
            :class="{ active: selectedPlan?.id === plan.id }"
            @click="selectPlan(plan)"
          >
            <img :src="plan.certificate_image_url" :alt="`${plan.certificate_name}封面`" />
            <div class="plan-row__body">
              <div><strong>{{ plan.certificate_name }}</strong><span>{{ sourceLabel(plan.generation_mode) }}</span></div>
              <p><el-icon><Calendar /></el-icon>{{ formatDate(plan.end_date) }}考试</p>
              <div class="progress-track"><i :style="{ width: `${plan.progress_percent}%` }"></i></div>
            </div>
            <div class="plan-row__today" :class="{ resting: !plan.today }">
              <strong>{{ plan.today ? `${plan.today.study_minutes}′` : '休' }}</strong>
              <span>{{ plan.today ? '今日' : '无任务' }}</span>
            </div>
          </button>
        </div>

        <div v-else-if="!loading" class="plan-empty">
          <span>还没有备考计划</span>
          <p>先从证书广场选择目标，让 AI 安排第一份计划。</p>
          <el-button type="primary" @click="router.push('/certificates')">去选择证书</el-button>
        </div>
      </aside>

      <main class="today-detail">
        <div v-if="!selectedPlan" class="detail-placeholder">
          <span class="placeholder-mark">今</span>
          <h3>选择一张证书</h3>
          <p>点击左侧计划查看今天的任务；再次点击同一计划可打开完整安排。</p>
        </div>

        <template v-else>
          <header class="detail-heading">
            <div>
              <span>{{ selectedPlan.today?.phase || '今日休息' }}</span>
              <h3>{{ selectedPlan.certificate_name }}</h3>
              <p v-if="selectedPlan.today">今天聚焦：{{ selectedPlan.today.focus }}</p>
              <p v-else>今天没有安排任务，保持节奏，下一学习日再继续。</p>
            </div>
            <el-button :loading="loadingFullPlan" @click="openFullPlan()">查看完整计划 <el-icon><ArrowRight /></el-icon></el-button>
          </header>

          <template v-if="selectedPlan.today">
            <div class="today-summary">
              <span><el-icon><Clock /></el-icon>{{ todayMinutes }} 分钟学习</span>
              <span>{{ todayTaskCount }} 项重点任务</span>
              <span>{{ selectedPlan.today.break_minutes }} 分钟休息</span>
            </div>
            <div class="today-route">
              <StudyTaskTimeline :tasks="selectedPlan.today.tasks" />
            </div>
          </template>

          <div v-else class="rest-day">
            <span>REST DAY</span>
            <strong>今天是计划内的休息日</strong>
            <p>可以回顾昨天的笔记，但不额外增加任务。</p>
          </div>
        </template>
      </main>
    </section>

    <StudyPlanDrawer v-model="drawerVisible" :plan="fullPlan" />
  </div>
</template>

<style scoped>
.today-page{width:min(1240px,100%);margin:0 auto;color:#17233c}.today-hero{min-height:188px;margin-bottom:22px;padding:28px 34px;display:flex;align-items:center;justify-content:space-between;gap:30px;overflow:hidden;position:relative;border:1px solid #fff;border-radius:22px;background:linear-gradient(118deg,#f8fbfe 0%,#edf3fb 70%,#e2ebfa 100%)}.today-hero:after{content:"TODAY";position:absolute;right:128px;bottom:-20px;color:rgb(49 87 213/5%);font:800 88px/1 "Avenir Next",sans-serif;letter-spacing:-.08em}.today-kicker{color:#3157d5;font:700 10px/1.4 "SFMono-Regular",monospace;letter-spacing:.14em}.today-hero h2{max-width:700px;margin:9px 0 8px;font:700 clamp(28px,3.3vw,43px)/1.18 "Songti SC",serif;letter-spacing:-.04em}.today-hero p{margin:0;color:#6d7c90;font-size:13px}.hero-ledger{min-width:112px;position:relative;z-index:1;text-align:right}.hero-ledger strong{display:block;color:#3157d5;font:700 43px/1 "Songti SC",serif}.hero-ledger span{color:#748399;font-size:10px}.training-workspace{min-height:470px;display:grid;grid-template-columns:minmax(290px,360px) minmax(0,1fr);gap:18px}.plan-index,.today-detail{border:1px solid rgb(255 255 255/92%);border-radius:20px;background:rgb(248 251 254/86%);box-shadow:0 14px 38px rgb(37 61 92/7%)}.plan-index{padding:22px 15px}.index-heading{padding:0 6px 14px;display:flex;align-items:end;justify-content:space-between;gap:12px}.index-heading span,.detail-heading>div>span,.rest-day>span{color:#3157d5;font:700 9px/1.4 "SFMono-Regular",monospace;letter-spacing:.14em}.index-heading h3{margin:5px 0 0;font:700 20px "Songti SC",serif}.index-heading small{color:#8a97a7;font-size:9px}.plan-list{display:grid;gap:7px}.plan-row{width:100%;padding:10px;display:grid;grid-template-columns:48px 1fr auto;gap:11px;align-items:center;border:1px solid transparent;border-radius:13px;background:transparent;color:inherit;text-align:left;cursor:pointer;transition:background .16s ease,border-color .16s ease,transform .16s ease}.plan-row:hover,.plan-row.active{border-color:#d7e1f5;background:#fff}.plan-row.active{box-shadow:0 8px 22px rgb(49 87 213/9%);transform:translateX(3px)}.plan-row:focus-visible{outline:3px solid rgb(49 87 213/25%);outline-offset:2px}.plan-row>img{width:48px;height:48px;border-radius:10px;object-fit:cover}.plan-row__body{min-width:0}.plan-row__body>div:first-child{display:flex;align-items:center;gap:7px}.plan-row__body strong{overflow:hidden;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.plan-row__body>div:first-child span{flex:none;padding:2px 5px;border-radius:4px;background:#e8edff;color:#3157d5;font-size:8px}.plan-row__body p{margin:5px 0 6px;display:flex;align-items:center;gap:3px;color:#7d8b9e;font-size:9px}.progress-track{height:3px;overflow:hidden;border-radius:10px;background:#e3e9f0}.progress-track i{height:100%;display:block;border-radius:inherit;background:#3157d5}.plan-row__today{display:grid;justify-items:center;gap:2px}.plan-row__today strong{color:#3157d5;font:700 15px "SFMono-Regular",monospace}.plan-row__today span{color:#8794a5;font-size:8px}.plan-row__today.resting strong{color:#4f9b77}.plan-empty,.detail-placeholder{height:100%;display:grid;place-content:center;justify-items:center;text-align:center}.plan-empty{min-height:300px;padding:28px}.plan-empty span{font:700 18px "Songti SC",serif}.plan-empty p{max-width:220px;margin:8px 0 18px;color:#78879a;font-size:11px;line-height:1.65}.today-detail{min-height:470px;padding:28px 30px}.detail-placeholder{min-height:410px}.placeholder-mark{width:58px;height:58px;display:grid;place-items:center;border:1px solid #d8e2ed;border-radius:50%;color:#3157d5;background:#f2f6fb;font:700 25px "Songti SC",serif}.detail-placeholder h3{margin:14px 0 6px;font:700 22px "Songti SC",serif}.detail-placeholder p{max-width:350px;margin:0;color:#7b899b;font-size:11px;line-height:1.7}.detail-heading{padding-bottom:18px;display:flex;align-items:start;justify-content:space-between;gap:20px;border-bottom:1px solid #e1e8ef}.detail-heading h3{margin:5px 0 4px;font:700 26px "Songti SC",serif}.detail-heading p{margin:0;color:#758497;font-size:11px}.detail-heading .el-button{flex:none}.today-summary{padding:14px 0;display:flex;gap:18px;border-bottom:1px solid #e1e8ef;color:#64758a;font-size:10px}.today-summary span{display:flex;align-items:center;gap:4px}.today-route{margin-top:22px;padding:20px 18px 8px;border-radius:14px;background:#f1f5f9}.rest-day{min-height:310px;display:grid;place-content:center;justify-items:center;text-align:center}.rest-day strong{margin-top:9px;font:700 24px "Songti SC",serif}.rest-day p{margin:7px 0 0;color:#7d8b9d;font-size:11px}@media(max-width:900px){.training-workspace{grid-template-columns:1fr}.plan-index{max-height:390px;overflow:auto}}@media(max-width:620px){.today-hero{min-height:160px;padding:24px;align-items:flex-start;flex-direction:column}.hero-ledger{text-align:left}.today-detail{padding:22px 18px}.detail-heading{flex-direction:column}.today-summary{gap:9px;flex-wrap:wrap}.training-workspace{gap:12px}}@media(prefers-reduced-motion:reduce){.plan-row{transition:none}}
</style>
