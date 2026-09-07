<script setup>
import { ArrowDown, ArrowLeft, ArrowRight, Calendar, Clock } from '@element-plus/icons-vue'
import { Editor as WangEditor, Toolbar as WangToolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import MarkdownIt from 'markdown-it'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import TurndownService from 'turndown'
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { useRouter } from 'vue-router'

import StudyTaskTimeline from '../components/StudyTaskTimeline.vue'
import { getDailySummary, getStudyCalendar, getStudyPlans, saveDailySummary, updateStudyTask } from '../services/api'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()
const plans = ref([])
const loading = ref(true)
const savingSummary = ref(false)
const updatingTaskId = ref(null)
const errorMessage = ref('')
const expandedPlanIds = ref([])
const summaryContent = ref('')
const summarySavedAt = ref('')
const summaryFormat = ref('markdown')
const wordEditorRef = shallowRef(null)
const calendarOpen = ref(false)
const calendarLoading = ref(false)
const calendarMonth = ref('')
const calendarStatus = ref({})
const markdownParser = new MarkdownIt({ html: false, linkify: true, breaks: true })
const turndownService = new TurndownService({
  headingStyle: 'atx',
  bulletListMarker: '-',
  codeBlockStyle: 'fenced',
})
const summaryToolbars = [
  'bold', 'italic', 'strikeThrough', '-', 'title', 'quote',
  'unorderedList', 'orderedList', 'task', 'link', 'table',
  '=', 'revoke', 'next', 'preview', 'previewOnly', 'save',
]
const summaryFooters = ['markdownTotal']
const calendarWeekdays = ['一', '二', '三', '四', '五', '六', '日']
const wordToolbarConfig = {
  excludeKeys: ['fullScreen', 'group-video', 'insertImage', 'uploadImage'],
}
const wordEditorConfig = {
  placeholder: '像使用 Word 一样记录今天的收获、问题和下一步行动……',
  scroll: true,
  maxLength: 50000,
}

function dateString(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const selectedDate = ref(dateString(new Date()))
const todayString = dateString(new Date())
calendarMonth.value = selectedDate.value.slice(0, 7)
const isToday = computed(() => selectedDate.value === todayString)
const selectedDateLabel = computed(() => new Intl.DateTimeFormat('zh-CN', {
  month: 'long', day: 'numeric', weekday: 'long',
}).format(new Date(`${selectedDate.value}T00:00:00`)))
const selectedDateButtonLabel = computed(() => {
  const [year, month, day] = selectedDate.value.split('-')
  return `${year}年${Number(month)}月${Number(day)}日`
})
const calendarMonthLabel = computed(() => {
  const [year, month] = calendarMonth.value.split('-')
  return `${year}年 ${Number(month)}月`
})
const calendarCells = computed(() => {
  const [year, month] = calendarMonth.value.split('-').map(Number)
  const firstDay = new Date(year, month - 1, 1)
  const gridStart = new Date(year, month - 1, 1 - ((firstDay.getDay() + 6) % 7))
  return Array.from({ length: 42 }, (_, index) => {
    const value = new Date(gridStart)
    value.setDate(gridStart.getDate() + index)
    const dateValue = dateString(value)
    return {
      date: dateValue,
      day: value.getDate(),
      inMonth: value.getMonth() === month - 1,
      isToday: dateValue === todayString,
      status: calendarStatus.value[dateValue] || null,
    }
  })
})
const datedPlans = computed(() => plans.value.filter((plan) => plan.today))
const studyTasks = computed(() => datedPlans.value.flatMap((plan) => plan.today.tasks.filter((task) => !task.is_break)))
const studyTaskCount = computed(() => studyTasks.value.length)
const completedTaskCount = computed(() => studyTasks.value.filter((task) => task.status === 'completed').length)
const studyMinutes = computed(() => datedPlans.value.reduce((total, plan) => total + plan.today.study_minutes, 0))
const breakMinutes = computed(() => datedPlans.value.reduce((total, plan) => total + plan.today.break_minutes, 0))

function sourceLabel(mode) {
  return { deepseek: 'DeepSeek', qwen: 'Qwen', ai: 'AI', rules: '智能规则' }[mode] || 'AI'
}

function openToday(plan) {
  router.push({ path: '/today', query: { plan: plan.id, date: selectedDate.value } })
}

function togglePlan(planId) {
  expandedPlanIds.value = expandedPlanIds.value.includes(planId)
    ? expandedPlanIds.value.filter((id) => id !== planId)
    : [...expandedPlanIds.value, planId]
}

function moveDate(offset) {
  const date = new Date(`${selectedDate.value}T00:00:00`)
  date.setDate(date.getDate() + offset)
  selectedDate.value = dateString(date)
}

function moveCalendarMonth(offset) {
  const [year, month] = calendarMonth.value.split('-').map(Number)
  const value = new Date(year, month - 1 + offset, 1)
  calendarMonth.value = dateString(value).slice(0, 7)
}

function selectCalendarDate(cell) {
  selectedDate.value = cell.date
  calendarMonth.value = cell.date.slice(0, 7)
  calendarOpen.value = false
}

async function loadCalendarStatus() {
  if (!calendarMonth.value) return
  calendarLoading.value = true
  try {
    const days = await getStudyCalendar(calendarMonth.value)
    calendarStatus.value = Object.fromEntries(days.map((item) => [item.study_date, item]))
  } catch {
    calendarStatus.value = {}
  } finally {
    calendarLoading.value = false
  }
}

function handleWordCreated(editor) {
  wordEditorRef.value = editor
}

function handleWordDestroyed() {
  wordEditorRef.value = null
}

function syncWordContent() {
  if (wordEditorRef.value) summaryContent.value = wordEditorRef.value.getHtml()
}

function handleWordChanged() {
  syncWordContent()
  summarySavedAt.value = ''
}

function changeSummaryFormat(nextFormat) {
  if (nextFormat === summaryFormat.value) return
  if (summaryFormat.value === 'word') {
    syncWordContent()
    summaryContent.value = turndownService.turndown(summaryContent.value)
  } else {
    summaryContent.value = markdownParser.render(summaryContent.value)
  }
  summaryFormat.value = nextFormat
  summarySavedAt.value = ''
}

async function toggleTask(task) {
  if (updatingTaskId.value) return
  updatingTaskId.value = task.id
  errorMessage.value = ''
  try {
    const result = await updateStudyTask(task.id, task.status !== 'completed')
    task.status = result.status
    await loadCalendarStatus()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    updatingTaskId.value = null
  }
}

async function saveSummary() {
  savingSummary.value = true
  errorMessage.value = ''
  try {
    if (summaryFormat.value === 'word') syncWordContent()
    const result = await saveDailySummary(selectedDate.value, summaryContent.value, summaryFormat.value)
    summaryContent.value = result.content
    summaryFormat.value = result.content_format
    summarySavedAt.value = '已保存'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    savingSummary.value = false
  }
}

async function loadDateData() {
  loading.value = true
  errorMessage.value = ''
  summarySavedAt.value = ''
  try {
    const [planData, summary] = await Promise.all([
      getStudyPlans(selectedDate.value),
      getDailySummary(selectedDate.value),
    ])
    plans.value = planData
    summaryContent.value = summary?.content || ''
    summaryFormat.value = summary?.content_format || 'markdown'
    const firstDatedPlan = planData.find((plan) => plan.today)
    expandedPlanIds.value = firstDatedPlan ? [firstDatedPlan.id] : []
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

watch(selectedDate, loadDateData, { immediate: true })
watch(selectedDate, (value) => {
  calendarMonth.value = value.slice(0, 7)
})
watch(calendarMonth, loadCalendarStatus, { immediate: true })
onBeforeUnmount(() => wordEditorRef.value?.destroy())
</script>

<template>
  <div class="todo-page">
    <section class="todo-heading">
      <div class="heading-copy">
        <span class="todo-kicker">{{ selectedDateLabel }} · {{ userStore.nickname }}</span>
        <h2>{{ isToday ? '我的代办' : '历史代办' }}</h2>
        <p>任务和总结都按日期保存，随时可以回来查看。</p>
      </div>

      <div class="date-navigator" aria-label="选择代办日期">
        <button type="button" aria-label="前一天" @click="moveDate(-1)"><el-icon><ArrowLeft /></el-icon></button>
        <el-popover
          v-model:visible="calendarOpen"
          placement="bottom-end"
          :width="336"
          trigger="click"
          :show-arrow="false"
          popper-class="todo-calendar-popper"
        >
          <template #reference>
            <button type="button" class="calendar-trigger" :aria-expanded="calendarOpen">
              <el-icon><Calendar /></el-icon>
              <span>{{ selectedDateButtonLabel }}</span>
            </button>
          </template>
          <div v-loading="calendarLoading" class="todo-calendar">
            <header>
              <button type="button" aria-label="上个月" @click="moveCalendarMonth(-1)"><el-icon><ArrowLeft /></el-icon></button>
              <strong>{{ calendarMonthLabel }}</strong>
              <button type="button" aria-label="下个月" @click="moveCalendarMonth(1)"><el-icon><ArrowRight /></el-icon></button>
            </header>
            <div class="calendar-weekdays" aria-hidden="true">
              <span v-for="weekday in calendarWeekdays" :key="weekday">{{ weekday }}</span>
            </div>
            <div class="calendar-grid" role="grid" :aria-label="`${calendarMonthLabel}训练日历`">
              <button
                v-for="cell in calendarCells"
                :key="cell.date"
                type="button"
                role="gridcell"
                :class="{
                  muted: !cell.inMonth,
                  selected: cell.date === selectedDate,
                  today: cell.isToday,
                  'has-tasks': cell.status,
                  completed: cell.status?.is_completed,
                }"
                :aria-label="`${cell.date}${cell.status?.is_completed ? '，任务已全部完成' : cell.status ? `，已完成${cell.status.completed_tasks}项，共${cell.status.total_tasks}项` : ''}`"
                @click="selectCalendarDate(cell)"
              >
                <span>{{ cell.day }}</span>
              </button>
            </div>
            <footer>
              <span><i class="pending-mark"></i>有待办</span>
              <span><i class="completed-mark"></i>已完成</span>
              <button type="button" @click="selectCalendarDate({ date: todayString })">回到今天</button>
            </footer>
          </div>
        </el-popover>
        <button type="button" aria-label="后一天" @click="moveDate(1)"><el-icon><ArrowRight /></el-icon></button>
        <button v-if="!isToday" type="button" class="back-today" @click="selectedDate = todayString">回到今天</button>
      </div>

      <div class="today-tally" aria-label="所选日期任务汇总">
        <span><strong>{{ completedTaskCount }}/{{ studyTaskCount }}</strong> 已完成</span>
        <i></i>
        <span><strong>{{ studyMinutes }}</strong> 分钟学习</span>
        <i></i>
        <span><strong>{{ breakMinutes }}</strong> 分钟休息</span>
      </div>
    </section>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

    <main v-loading="loading" class="todo-ledger">
      <template v-if="datedPlans.length">
        <article v-for="(plan, index) in datedPlans" :key="plan.id" class="todo-plan">
          <header>
            <button type="button" class="plan-toggle" :aria-expanded="expandedPlanIds.includes(plan.id)" @click="togglePlan(plan.id)">
              <span class="plan-sequence">{{ String(index + 1).padStart(2, '0') }}</span>
              <img :src="plan.certificate_image_url" :alt="`${plan.certificate_name}封面`" />
              <span class="plan-identity">
                <small>{{ plan.today.phase }} · {{ sourceLabel(plan.generation_mode) }}</small>
                <strong>{{ plan.certificate_name }}</strong>
                <span>当日重点：{{ plan.today.focus }}</span>
              </span>
              <span class="plan-budget">
                <small><el-icon><Clock /></el-icon>{{ plan.today.study_minutes }} 分钟</small>
                <small><el-icon><Calendar /></el-icon>DAY {{ String(plan.today.day_number).padStart(2, '0') }}</small>
              </span>
              <el-icon class="toggle-icon" :class="{ open: expandedPlanIds.includes(plan.id) }"><ArrowDown /></el-icon>
            </button>
            <el-button text @click="openToday(plan)">进入训练 <el-icon><ArrowRight /></el-icon></el-button>
          </header>
          <el-collapse-transition>
            <div v-show="expandedPlanIds.includes(plan.id)" class="todo-task-list">
              <StudyTaskTimeline :tasks="plan.today.tasks" checkable :updating-task-id="updatingTaskId" @toggle="toggleTask" />
            </div>
          </el-collapse-transition>
        </article>
      </template>

      <div v-else-if="!loading" class="todo-empty">
        <span>{{ isToday ? '今日清单为空' : '当日清单为空' }}</span>
        <h3>这一天没有计划内任务</h3>
        <p v-if="plans.length">这是计划内的休息日，可以记录总结，但不必额外增加任务。</p>
        <p v-else>当前还没有备考计划，可以先从证书广场选择目标。</p>
        <el-button v-if="!plans.length" type="primary" @click="router.push('/certificates')">去证书广场</el-button>
      </div>
    </main>

    <section class="daily-summary">
      <header>
        <div><span>DAILY NOTE</span><h3>{{ isToday ? '今日总结' : '当日总结' }}</h3></div>
        <div class="summary-actions">
          <small>{{ summarySavedAt || `${selectedDateLabel}的记录` }}</small>
          <div class="summary-mode-switch" role="tablist" aria-label="总结编辑方式">
            <button type="button" role="tab" :aria-selected="summaryFormat === 'markdown'" :class="{ active: summaryFormat === 'markdown' }" @click="changeSummaryFormat('markdown')">Markdown</button>
            <button type="button" role="tab" :aria-selected="summaryFormat === 'word'" :class="{ active: summaryFormat === 'word' }" @click="changeSummaryFormat('word')">Word</button>
          </div>
        </div>
      </header>
      <MdEditor
        v-show="summaryFormat === 'markdown'"
        v-model="summaryContent"
        class="summary-editor"
        language="zh-CN"
        preview-theme="smart-blue"
        :toolbars="summaryToolbars"
        :footers="summaryFooters"
        :max-length="50000"
        :no-upload-img="true"
        :no-katex="true"
        :no-mermaid="true"
        :no-echarts="true"
        :no-highlight="true"
        placeholder="用 Markdown 记录今天的收获、问题和下一步行动……"
        @onChange="summarySavedAt = ''"
        @onSave="saveSummary"
      />
      <div v-if="summaryFormat === 'word'" class="word-editor-shell">
        <WangToolbar
          class="word-editor-toolbar"
          :editor="wordEditorRef"
          :default-config="wordToolbarConfig"
          mode="default"
        />
        <WangEditor
          v-model="summaryContent"
          class="word-editor-content"
          :default-config="wordEditorConfig"
          mode="default"
          @on-created="handleWordCreated"
          @on-destroyed="handleWordDestroyed"
          @on-change="handleWordChanged"
        />
      </div>
      <footer>
        <p>{{ summaryFormat === 'markdown' ? 'Markdown 模式适合结构化复盘。' : 'Word 模式适合直接排版和所见即所得编辑。' }}</p>
        <el-button type="primary" :loading="savingSummary" @click="saveSummary">保存总结</el-button>
      </footer>
    </section>
  </div>
</template>

<style scoped>
.todo-page{width:min(1180px,100%);margin:0 auto;color:#17233c}.todo-heading{min-height:154px;margin-bottom:18px;padding:24px 28px;display:grid;grid-template-columns:1fr auto;gap:20px 28px;align-items:center;border:1px solid #fff;border-radius:20px;background:rgb(248 251 254/88%)}.heading-copy{min-width:0}.todo-kicker{color:#3157d5;font:700 10px/1.4 "SFMono-Regular",monospace;letter-spacing:.13em}.todo-heading h2{margin:5px 0 4px;font:700 32px/1.15 "Songti SC",serif}.todo-heading p{margin:0;color:#718095;font-size:11px}.date-navigator{display:flex;align-items:center;gap:6px}.date-navigator>button{height:32px;padding:0 9px;display:grid;place-items:center;border:1px solid #d9e2ec;border-radius:8px;background:#fff;color:#52677f;cursor:pointer}.date-navigator .back-today{color:#3157d5;font-size:10px;font-weight:700}.date-navigator :deep(.el-date-editor){width:174px}.today-tally{grid-column:1/-1;padding-top:15px;display:flex;align-items:center;gap:15px;border-top:1px solid #e1e8ef;color:#748399;font-size:9px}.today-tally span{display:flex;align-items:baseline;gap:4px}.today-tally strong{color:#17233c;font:700 14px "SFMono-Regular",monospace}.today-tally i{width:1px;height:18px;background:#dbe4ed}.todo-ledger{min-height:260px}.todo-plan{margin-bottom:10px;overflow:hidden;border:1px solid rgb(255 255 255/92%);border-radius:16px;background:rgb(248 251 254/88%);box-shadow:0 10px 28px rgb(37 61 92/6%)}.todo-plan>header{padding:11px 13px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center}.plan-toggle{min-width:0;padding:0;display:grid;grid-template-columns:28px 48px minmax(0,1fr) auto 18px;gap:12px;align-items:center;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer}.plan-toggle:focus-visible,.date-navigator>button:focus-visible{outline:3px solid rgb(49 87 213/24%);outline-offset:2px}.plan-sequence{color:#93a0b0;font:700 10px "SFMono-Regular",monospace}.plan-toggle img{width:48px;height:48px;border-radius:10px;object-fit:cover}.plan-identity{min-width:0;display:grid;gap:2px}.plan-identity>small{color:#3157d5;font:700 8px "SFMono-Regular",monospace;letter-spacing:.08em}.plan-identity>strong{overflow:hidden;font:700 15px "Songti SC",serif;text-overflow:ellipsis;white-space:nowrap}.plan-identity>span{overflow:hidden;color:#78879a;font-size:9px;text-overflow:ellipsis;white-space:nowrap}.plan-budget{display:flex;gap:12px;color:#6f7f93}.plan-budget small{display:flex;align-items:center;gap:3px;font-size:9px}.toggle-icon{color:#8290a2;transition:transform .18s ease}.toggle-icon.open{transform:rotate(180deg)}.todo-plan>header>.el-button{color:#3157d5}.todo-task-list{padding:17px 22px 6px;border-top:1px solid #e4eaf0;background:#f2f6fa}.todo-empty{min-height:260px;display:grid;place-content:center;justify-items:center;text-align:center;border:1px solid #fff;border-radius:18px;background:rgb(248 251 254/82%)}.todo-empty>span,.daily-summary header span{color:#3157d5;font:700 9px "SFMono-Regular",monospace;letter-spacing:.13em}.todo-empty h3{margin:8px 0 5px;font:700 23px "Songti SC",serif}.todo-empty p{max-width:380px;margin:0 0 16px;color:#78879a;font-size:10px;line-height:1.7}.daily-summary{margin-top:18px;padding:23px 25px;border:1px solid #fff;border-radius:18px;background:rgb(248 251 254/88%);box-shadow:0 10px 28px rgb(37 61 92/5%)}.daily-summary>header{margin-bottom:14px;display:flex;align-items:end;justify-content:space-between;gap:15px}.daily-summary h3{margin:4px 0 0;font:700 23px "Songti SC",serif}.summary-actions{display:flex;align-items:center;gap:12px}.summary-actions>small{color:#8491a2;font-size:9px}.summary-mode-switch{padding:3px;display:flex;gap:2px;border:1px solid #dce4ed;border-radius:9px;background:#edf2f7}.summary-mode-switch button{height:27px;padding:0 11px;border:0;border-radius:6px;background:transparent;color:#748399;font-size:10px;font-weight:700;cursor:pointer;transition:background-color .16s ease,color .16s ease,box-shadow .16s ease}.summary-mode-switch button.active{background:#fff;color:#3157d5;box-shadow:0 3px 9px rgb(38 61 91/10%)}.summary-mode-switch button:focus-visible{outline:3px solid rgb(49 87 213/22%);outline-offset:2px}.daily-summary :deep(.summary-editor.md-editor){height:280px;overflow:hidden;border:1px solid #dce4ed;border-radius:12px;--md-color:#566980;--md-bk-color:#f6f9fc;--md-bk-color-outstand:#e9eff8;--md-bk-hover-color:#edf2fa;--md-border-color:#dce4ed;--md-border-hover-color:#b9c8dc;--md-border-active-color:#3157d5}.daily-summary :deep(.summary-editor .md-editor-toolbar-wrapper){padding:5px 7px;background:#fff}.daily-summary :deep(.summary-editor .md-editor-toolbar-item){border-radius:6px}.daily-summary :deep(.summary-editor .md-editor-input-wrapper),.daily-summary :deep(.summary-editor .md-editor-preview-wrapper){background:#f6f9fc}.daily-summary :deep(.summary-editor .cm-content){padding:15px 16px;font:400 13px/1.75 "PingFang SC",sans-serif}.daily-summary :deep(.summary-editor .md-editor-preview){padding:15px 18px;font-size:13px;line-height:1.75}.daily-summary :deep(.summary-editor .md-editor-footer){height:25px;background:#fff;color:#8a97a8}.word-editor-shell{height:420px;overflow:hidden;border:1px solid #dce4ed;border-radius:12px;background:#f2f5f8}.word-editor-shell :deep(.umo-editor-container){min-height:400px;--umo-primary-color:#3157d5;--umo-container-background:#eef3f8}.word-editor-shell :deep(.umo-toolbar){border-color:#dce4ed}.daily-summary>footer{margin-top:12px;display:flex;align-items:center;justify-content:space-between;gap:15px}.daily-summary footer p{margin:0;color:#8190a2;font-size:10px}@media(max-width:900px){.todo-heading{grid-template-columns:1fr}.today-tally{grid-column:1}.date-navigator{grid-row:2}.plan-toggle{grid-template-columns:24px 44px 1fr}.plan-budget,.toggle-icon{grid-column:3}.plan-budget{justify-content:flex-start}.toggle-icon{justify-self:end;grid-row:1/3}.todo-plan>header{align-items:start}}@media(max-width:620px){.todo-heading{padding:20px}.date-navigator{flex-wrap:wrap}.today-tally{gap:9px;flex-wrap:wrap}.plan-toggle{grid-template-columns:42px 1fr}.plan-sequence{display:none}.plan-toggle img{width:42px;height:42px}.plan-identity,.plan-budget,.toggle-icon{grid-column:2}.toggle-icon{grid-row:1;align-self:center}.todo-plan>header{grid-template-columns:1fr}.todo-plan>header>.el-button{justify-self:end}.todo-task-list{padding:15px 12px 5px}.daily-summary{padding:20px}.daily-summary>header{align-items:flex-start;flex-direction:column}.summary-actions{width:100%;justify-content:space-between}.daily-summary :deep(.summary-editor.md-editor){height:340px}.word-editor-shell{height:480px}.daily-summary>footer{align-items:flex-start;flex-direction:column}}@media(prefers-reduced-motion:reduce){.toggle-icon,.summary-mode-switch button{transition:none}}
.word-editor-shell{background:#f6f9fc}
.word-editor-toolbar{border-bottom:1px solid #dce4ed;background:#fff}
.word-editor-content{height:377px;overflow-y:auto;background:#f6f9fc}
.word-editor-shell :deep(.w-e-toolbar){background:#fff}
.word-editor-shell :deep(.w-e-text-container){background:#f6f9fc}
.word-editor-shell :deep(.w-e-text-placeholder){left:16px;top:16px;color:#9aa7b7;font-size:13px;font-style:normal;line-height:1.75}
.word-editor-shell :deep(.w-e-text-container:focus-within .w-e-text-placeholder){display:none}
.word-editor-shell :deep([data-slate-editor]){min-height:310px;padding:0 16px;font:400 13px/1.75 "PingFang SC",sans-serif}
.date-navigator>.calendar-trigger{width:176px;padding:0 11px;display:flex;grid-auto-flow:unset;place-items:unset;align-items:center;gap:8px;color:#4f6178;font-size:11px}.calendar-trigger span{flex:1;text-align:left}.calendar-trigger[aria-expanded=true]{border-color:#3157d5;box-shadow:0 0 0 3px rgb(49 87 213/10%)}
:global(.todo-calendar-popper.el-popover){padding:12px;border:1px solid #dce5ef;border-radius:16px;box-shadow:0 18px 45px rgb(30 54 84/18%)}
.todo-calendar{min-height:354px;color:#24344d}.todo-calendar>header{height:42px;padding:0 4px 9px;display:grid;grid-template-columns:32px 1fr 32px;align-items:center;border-bottom:1px solid #e8edf3}.todo-calendar>header strong{text-align:center;font:700 15px/1 "Songti SC",serif}.todo-calendar>header button{width:30px;height:30px;display:grid;place-items:center;border:0;border-radius:8px;background:transparent;color:#6f8095;cursor:pointer}.todo-calendar>header button:hover{background:#edf2fb;color:#3157d5}.calendar-weekdays,.calendar-grid{display:grid;grid-template-columns:repeat(7,1fr)}.calendar-weekdays{padding:10px 2px 5px}.calendar-weekdays span{text-align:center;color:#98a5b5;font:700 9px/1.4 "SFMono-Regular",monospace}.calendar-grid{gap:3px}.calendar-grid button{position:relative;height:37px;display:grid;place-items:center;border:0;border-radius:10px;background:transparent;color:#33445c;font:600 11px/1 "SFMono-Regular",monospace;cursor:pointer}.calendar-grid button:hover{background:#edf2fb;color:#3157d5}.calendar-grid button.muted{color:#c2cad4}.calendar-grid button.today{box-shadow:inset 0 0 0 1px #9eb2e8}.calendar-grid button.selected{background:#3157d5;color:#fff;box-shadow:none}.calendar-grid button>span{position:relative;z-index:1}.calendar-grid button.has-tasks:not(.completed)::after{content:"";position:absolute;bottom:5px;width:4px;height:4px;border-radius:50%;background:#3157d5}.calendar-grid button.selected.has-tasks:not(.completed)::after{background:#fff}.calendar-grid button.completed{color:#31906d;background:#edf8f3}.calendar-grid button.completed>span::after{content:"";position:absolute;left:50%;top:50%;width:25px;height:2px;border-radius:2px;background:#3aaa7f;transform:translate(-50%,-50%) rotate(-38deg);box-shadow:0 0 0 1px rgb(255 255 255/65%)}.calendar-grid button.selected.completed{background:#3157d5;color:#fff}.calendar-grid button.selected.completed>span::after{background:#9ee4c9;box-shadow:none}.todo-calendar>footer{margin-top:10px;padding:10px 5px 1px;display:flex;align-items:center;gap:14px;border-top:1px solid #e8edf3;color:#8391a3;font-size:9px}.todo-calendar>footer span{display:flex;align-items:center;gap:5px}.todo-calendar>footer i{position:relative;width:9px;height:9px;display:inline-block}.pending-mark{border-radius:50%;background:#3157d5}.completed-mark{border-radius:3px;background:#edf8f3}.completed-mark::after{content:"";position:absolute;left:-1px;top:4px;width:11px;height:2px;border-radius:2px;background:#3aaa7f;transform:rotate(-38deg)}.todo-calendar>footer button{margin-left:auto;padding:0;border:0;background:transparent;color:#3157d5;font-size:9px;font-weight:700;cursor:pointer}
.calendar-grid button.completed>span::after{transform:translate(-50%,-50%) rotate(38deg)}
.completed-mark::after{transform:rotate(38deg)}
</style>
