<script setup>
import { computed, ref, watch } from 'vue'

import StudyTaskTimeline from './StudyTaskTimeline.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  plan: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])
const selectedPhase = ref('all')
const activeDayIds = ref([])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})
const firstStudyDay = computed(() => props.plan?.days?.[0] || null)
const totalBreakMinutes = computed(() => props.plan?.outline?.reduce((total, phase) => total + phase.break_minutes, 0) || 0)
const filteredDays = computed(() => {
  const days = props.plan?.days || []
  return selectedPhase.value === 'all' ? days : days.filter((day) => day.phase === selectedPhase.value)
})

watch(() => props.plan?.id, () => {
  selectedPhase.value = 'all'
  activeDayIds.value = props.plan?.days?.length ? [props.plan.days[0].id] : []
})

function formatDate(value) {
  if (!value) return ''
  const [, month, day] = value.split('-')
  return `${Number(month)}月${Number(day)}日`
}

function planSourceLabel(mode) {
  return { deepseek: 'DeepSeek 已生成', qwen: 'Qwen 已生成', ai: 'AI 已生成', rules: '智能规则已生成' }[mode] || '计划已生成'
}
</script>

<template>
  <el-drawer v-model="visible" size="min(860px, 100vw)" class="plan-result-drawer">
    <template #header>
      <div class="plan-dialog-heading">
        <span class="drawer-kicker">{{ planSourceLabel(plan?.generation_mode) }}</span>
        <h3>{{ plan?.name }}</h3>
        <p>先看清整条路线，再专注完成眼前这一项。</p>
      </div>
    </template>

    <div v-if="plan" class="plan-result">
      <section class="plan-briefing">
        <div class="plan-briefing__period">
          <span>备考周期</span>
          <strong>{{ formatDate(plan.start_date) }} <i>→</i> {{ formatDate(plan.end_date) }}</strong>
        </div>
        <dl>
          <div><dt>学习日</dt><dd>{{ plan.total_days }} 天</dd></div>
          <div><dt>有效学习</dt><dd>{{ Math.round(plan.total_study_minutes / 60) }} 小时</dd></div>
          <div><dt>计划休息</dt><dd>{{ totalBreakMinutes }} 分钟</dd></div>
        </dl>
      </section>

      <section class="route-section">
        <div class="section-heading">
          <div><span>THE ROUTE</span><h4>总体学习大纲</h4></div>
          <p>三个阶段依次推进，宽度代表各阶段学习天数。</p>
        </div>
        <div class="study-route">
          <button
            v-for="(phase, index) in plan.outline"
            :key="phase.phase"
            type="button"
            :class="{ active: selectedPhase === phase.phase }"
            :style="{ flexGrow: phase.study_days }"
            @click="selectedPhase = phase.phase"
          >
            <span>阶段 0{{ index + 1 }}</span>
            <strong>{{ phase.phase }}</strong>
            <small>{{ phase.study_days }} 天 · {{ Math.round(phase.study_minutes / 60) }} 小时</small>
            <i aria-hidden="true"></i>
          </button>
        </div>
        <div class="route-notes">
          <article v-for="phase in plan.outline" :key="phase.phase">
            <span>{{ formatDate(phase.start_date) }}—{{ formatDate(phase.end_date) }}</span>
            <strong>{{ phase.phase }}</strong>
            <p>{{ phase.subjects.join('、') }}</p>
          </article>
        </div>
      </section>

      <section v-if="firstStudyDay" class="first-mission">
        <div class="first-mission__heading">
          <div><span>从这里开始</span><h4>{{ formatDate(firstStudyDay.study_date) }} · {{ firstStudyDay.focus }}</h4></div>
          <small>DAY {{ String(firstStudyDay.day_number).padStart(2, '0') }}</small>
        </div>
        <StudyTaskTimeline :tasks="firstStudyDay.tasks" tone="dark" />
      </section>

      <section class="full-schedule">
        <div class="section-heading section-heading--schedule">
          <div><span>DAILY PLAN</span><h4>完整每日安排</h4></div>
          <p>共 {{ plan.days.length }} 天，按日期展开查看分钟级任务。</p>
        </div>
        <div class="phase-filter" aria-label="按学习阶段筛选">
          <button type="button" :class="{ active: selectedPhase === 'all' }" @click="selectedPhase = 'all'">全部 {{ plan.days.length }}</button>
          <button v-for="phase in plan.outline" :key="phase.phase" type="button" :class="{ active: selectedPhase === phase.phase }" @click="selectedPhase = phase.phase">{{ phase.phase }} {{ phase.study_days }}</button>
        </div>

        <el-collapse v-model="activeDayIds" class="day-collapse">
          <el-collapse-item v-for="day in filteredDays" :key="day.id" :name="day.id">
            <template #title>
              <div class="day-title">
                <span>DAY {{ String(day.day_number).padStart(2, '0') }}</span>
                <time>{{ formatDate(day.study_date) }}</time>
                <strong>{{ day.focus }}</strong>
                <small>{{ day.study_minutes }} 分钟</small>
              </div>
            </template>
            <div class="day-task-list"><StudyTaskTimeline :tasks="day.tasks" /></div>
          </el-collapse-item>
        </el-collapse>
      </section>
    </div>
  </el-drawer>
</template>

<style scoped>
.plan-result{--plan-ink:#17233c;--plan-blue:#3157d5;--plan-coral:#ff8466;--plan-paper:#f4f7fa;--plan-line:#dfe7ef;--plan-muted:#718095;color:var(--plan-ink)}.drawer-kicker{color:#3157d5;font:700 11px/1.4 "SFMono-Regular",monospace;letter-spacing:.14em}.plan-dialog-heading h3{margin:7px 0 6px;font:700 28px/1.3 "Songti SC",serif}.plan-dialog-heading p{margin:0;color:#718095;font-size:13px}.plan-briefing{padding:24px 26px;display:flex;align-items:flex-end;justify-content:space-between;gap:28px;background:var(--plan-paper);border:1px solid var(--plan-line);border-radius:18px;color:var(--plan-ink)}.plan-briefing__period{display:grid;gap:7px}.plan-briefing__period>span{color:var(--plan-blue);font:700 10px/1.4 "SFMono-Regular",monospace;letter-spacing:.14em}.plan-briefing__period strong{font:700 25px/1.2 "Songti SC",serif}.plan-briefing__period i{padding:0 8px;color:var(--plan-coral);font-style:normal}.plan-briefing dl{margin:0;display:flex;gap:22px}.plan-briefing dl>div{display:grid;gap:4px}.plan-briefing dt{color:#7b899b;font-size:10px}.plan-briefing dd{margin:0;color:#30435b;font-size:13px;font-weight:700}.route-section,.first-mission,.full-schedule{margin-top:34px}.section-heading{margin-bottom:17px;display:flex;align-items:end;justify-content:space-between;gap:20px}.section-heading span{color:var(--plan-blue);font:700 9px/1.4 "SFMono-Regular",monospace;letter-spacing:.16em}.section-heading h4{margin:4px 0 0;font:700 22px/1.25 "Songti SC",serif}.section-heading p{max-width:310px;margin:0;color:var(--plan-muted);font-size:11px;text-align:right;line-height:1.6}.study-route{display:flex;gap:5px}.study-route button{min-width:128px;padding:15px 14px 14px;display:grid;gap:5px;position:relative;overflow:hidden;border:1px solid var(--plan-line);border-radius:11px;background:#fff;color:var(--plan-ink);text-align:left;cursor:pointer;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}.study-route button:hover,.study-route button.active{z-index:1;border-color:#8da4ef;box-shadow:0 9px 24px rgb(49 87 213/11%);transform:translateY(-2px)}.study-route button:focus-visible,.phase-filter button:focus-visible{outline:3px solid rgb(49 87 213/24%);outline-offset:2px}.study-route button>span{color:#8996a7;font:700 9px monospace;letter-spacing:.08em}.study-route button>strong{font:700 14px "Songti SC",serif}.study-route button>small{color:var(--plan-muted);font-size:9px}.study-route button>i{height:4px;margin-top:7px;display:block;border-radius:9px;background:var(--plan-blue)}.study-route button:nth-child(2)>i{background:#7b69ca}.study-route button:nth-child(3)>i{background:var(--plan-coral)}.route-notes{margin-top:10px;display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--plan-line);border-radius:12px;overflow:hidden}.route-notes article{min-width:0;padding:13px 15px;background:var(--plan-paper);border-right:1px solid var(--plan-line)}.route-notes article:last-child{border-right:0}.route-notes span{display:block;color:#8693a4;font:700 9px monospace}.route-notes strong{display:block;margin:5px 0;color:#3d5069;font-size:11px}.route-notes p{margin:0;overflow:hidden;color:#76869a;font-size:10px;line-height:1.5;text-overflow:ellipsis;white-space:nowrap}.first-mission{padding:24px 25px;background:var(--plan-ink);border-radius:18px;color:#fff;box-shadow:0 18px 42px rgb(23 35 60/16%)}.first-mission__heading{padding-bottom:16px;display:flex;align-items:start;justify-content:space-between;border-bottom:1px solid rgb(255 255 255/12%)}.first-mission__heading span{color:var(--plan-coral);font:700 10px monospace;letter-spacing:.12em}.first-mission__heading h4{margin:6px 0 0;font:700 22px "Songti SC",serif}.first-mission__heading>small{color:#95a6bd;font:700 11px monospace}.first-mission :deep(.study-task-timeline){padding-top:13px}.section-heading--schedule{margin-bottom:12px}.phase-filter{margin-bottom:12px;display:flex;gap:7px;overflow-x:auto;scrollbar-width:none}.phase-filter button{flex:none;padding:7px 10px;border:1px solid var(--plan-line);border-radius:8px;background:#fff;color:#66778c;font-size:10px;cursor:pointer}.phase-filter button.active{border-color:var(--plan-blue);background:var(--plan-blue);color:#fff}.day-collapse{border-top:1px solid var(--plan-line)!important}.day-collapse :deep(.el-collapse-item__header){height:auto;min-height:62px;padding:0 10px;background:transparent;border-color:var(--plan-line)}.day-collapse :deep(.el-collapse-item__wrap){background:transparent;border-color:var(--plan-line)}.day-collapse :deep(.el-collapse-item__content){padding:4px 10px 18px}.day-title{width:100%;display:grid;grid-template-columns:62px 64px 1fr auto;gap:12px;align-items:center}.day-title>span{color:var(--plan-blue);font:700 9px monospace}.day-title>time{color:#7f8da0;font:700 10px monospace}.day-title>strong{overflow:hidden;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.day-title>small{color:#8795a5;font-size:9px}.day-task-list{padding:12px 14px;background:var(--plan-paper);border-radius:12px}@media(max-width:680px){.plan-briefing{align-items:flex-start;flex-direction:column}.plan-briefing dl{width:100%;justify-content:space-between}.study-route{display:grid;grid-template-columns:1fr}.route-notes{grid-template-columns:1fr}.route-notes article{border-right:0;border-bottom:1px solid var(--plan-line)}.route-notes article:last-child{border-bottom:0}.section-heading{align-items:start;flex-direction:column}.section-heading p{text-align:left}.day-title{grid-template-columns:56px 58px 1fr}.day-title>small{display:none}}@media(prefers-reduced-motion:reduce){.study-route button{transition:none}}
</style>
