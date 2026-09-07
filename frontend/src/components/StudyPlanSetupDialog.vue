<script setup>
import { MagicStick } from '@element-plus/icons-vue'
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  certificate: { type: Object, default: null },
  generating: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'generate'])
const localError = ref('')
const weekdayOptions = [
  { label: '周一', value: 1 }, { label: '周二', value: 2 }, { label: '周三', value: 3 },
  { label: '周四', value: 4 }, { label: '周五', value: 5 }, { label: '周六', value: 6 },
  { label: '周日', value: 7 },
]
const dailyMinuteOptions = Array.from({ length: 31 }, (_, index) => 30 + index * 15)
const sessionMinuteOptions = [20, 25, 30, 35, 40, 45, 50, 60, 75, 90]
const breakMinuteOptions = [5, 10, 15, 20, 25, 30]
const levelOptions = [
  { label: '零基础', value: 'beginner' },
  { label: '了解一些', value: 'basic' },
  { label: '学过一轮', value: 'intermediate' },
  { label: '冲刺提分', value: 'advanced' },
]
const form = reactive({
  ai_provider: 'deepseek', target_exam_date: '', study_start_date: '',
  weekday_minutes: 90, weekend_minutes: 150, current_level: 'beginner',
  weak_subjects: [], preferred_period: 'evening', session_minutes: 40,
  break_minutes: 10, available_weekdays: [1, 2, 3, 4, 5, 6, 7],
})

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})
const prepDays = computed(() => {
  if (!form.target_exam_date || !form.study_start_date) return 0
  return Math.max(Math.ceil((new Date(form.target_exam_date) - new Date(form.study_start_date)) / 86400000), 0)
})
const displayedError = computed(() => localError.value || props.errorMessage)

function dateString(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function resetForm() {
  if (!props.certificate) return
  const startDate = new Date()
  const examDate = new Date()
  const recommendedDays = Number(props.certificate.recommended_days) || 60
  examDate.setDate(examDate.getDate() + recommendedDays)
  Object.assign(form, {
    ai_provider: 'deepseek', target_exam_date: dateString(examDate), study_start_date: dateString(startDate),
    weekday_minutes: props.certificate.recommended_daily_minutes,
    weekend_minutes: Math.min(Math.round(props.certificate.recommended_daily_minutes * 1.5), 480),
    current_level: 'beginner', weak_subjects: [], preferred_period: 'evening',
    session_minutes: 40, break_minutes: 10, available_weekdays: [1, 2, 3, 4, 5, 6, 7],
  })
  localError.value = ''
}

function submitPlan() {
  if (prepDays.value < 3) {
    localError.value = '考试日期至少需要晚于开始日期 3 天'
    return
  }
  localError.value = ''
  emit('generate', { ...form, weak_subjects: [...form.weak_subjects], available_weekdays: [...form.available_weekdays] })
}

watch(() => [props.modelValue, props.certificate?.id], ([isOpen]) => {
  if (isOpen) resetForm()
})
</script>

<template>
  <el-dialog v-model="visible" width="min(720px, calc(100vw - 30px))" class="plan-setup-dialog" destroy-on-close @open="resetForm">
    <template #header>
      <div class="plan-dialog-heading">
        <span class="dialog-kicker">生成个人计划</span>
        <h3>{{ certificate?.short_name || certificate?.name }}</h3>
        <p>再补充几项情况，教练会把学习与休息安排到每一分钟。</p>
      </div>
    </template>

    <el-form label-position="top" class="plan-form">
      <section class="form-section">
        <header><span>01</span><div><strong>考试目标</strong><small>确定计划的起点和截止日期</small></div></header>
        <div class="plan-form-grid">
          <el-form-item label="开始复习日期"><el-date-picker v-model="form.study_start_date" type="date" value-format="YYYY-MM-DD" :clearable="false" /></el-form-item>
          <el-form-item label="预计考试日期"><el-date-picker v-model="form.target_exam_date" type="date" value-format="YYYY-MM-DD" :clearable="false" /></el-form-item>
        </div>
        <div class="prep-summary"><span>备考周期</span><strong>{{ prepDays }}</strong><span>天</span><i>系统会根据这个周期拆分大纲和每日任务</i></div>
      </section>

      <section class="form-section">
        <header><span>02</span><div><strong>学习情况</strong><small>让内容难度更贴近你现在的基础</small></div></header>
        <div class="plan-form-grid">
          <el-form-item label="目前基础">
            <el-select v-model="form.current_level" placeholder="选择当前基础">
              <el-option v-for="option in levelOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="规划模型">
            <el-select v-model="form.ai_provider" placeholder="选择规划模型">
              <el-option label="DeepSeek V4 Flash" value="deepseek" />
              <el-option label="Qwen3.7 Max" value="qwen" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="比较薄弱的科目（可多选）">
          <el-select v-model="form.weak_subjects" multiple collapse-tags collapse-tags-tooltip clearable placeholder="暂时不确定可以留空">
            <el-option v-for="subject in certificate?.subjects || []" :key="subject" :label="subject" :value="subject" />
          </el-select>
        </el-form-item>
      </section>

      <section class="form-section">
        <header><span>03</span><div><strong>可用时间</strong><small>所有时长都以分钟为单位</small></div></header>
        <div class="plan-form-grid">
          <el-form-item label="工作日每天可学习">
            <el-select v-model="form.weekday_minutes">
              <el-option v-for="minutes in dailyMinuteOptions.filter((item) => item <= 360)" :key="minutes" :label="`${minutes} 分钟/天`" :value="minutes" />
            </el-select>
          </el-form-item>
          <el-form-item label="周末每天可学习">
            <el-select v-model="form.weekend_minutes">
              <el-option v-for="minutes in dailyMinuteOptions" :key="minutes" :label="`${minutes} 分钟/天`" :value="minutes" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="每周可以学习的日期">
          <el-select v-model="form.available_weekdays" multiple collapse-tags collapse-tags-tooltip placeholder="选择学习日">
            <el-option v-for="day in weekdayOptions" :key="day.value" :label="day.label" :value="day.value" />
          </el-select>
        </el-form-item>
        <div class="plan-form-grid plan-form-grid--three">
          <el-form-item label="习惯学习时间">
            <el-select v-model="form.preferred_period"><el-option label="早晨" value="morning" /><el-option label="下午" value="afternoon" /><el-option label="晚上" value="evening" /></el-select>
          </el-form-item>
          <el-form-item label="单次专注时长">
            <el-select v-model="form.session_minutes"><el-option v-for="minutes in sessionMinuteOptions" :key="minutes" :label="`${minutes} 分钟`" :value="minutes" /></el-select>
          </el-form-item>
          <el-form-item label="每次休息时长">
            <el-select v-model="form.break_minutes"><el-option v-for="minutes in breakMinuteOptions" :key="minutes" :label="`${minutes} 分钟`" :value="minutes" /></el-select>
          </el-form-item>
        </div>
      </section>
    </el-form>

    <el-alert v-if="displayedError" :title="displayedError" type="error" show-icon :closable="false" />
    <template #footer>
      <el-button @click="visible = false">稍后再说</el-button>
      <el-button type="primary" :loading="generating" :icon="MagicStick" @click="submitPlan">生成每日计划</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-kicker{color:#3157d5;font:700 10px/1.4 "SFMono-Regular",monospace;letter-spacing:.15em}.plan-dialog-heading h3{margin:7px 0 5px;color:#17233c;font:700 27px/1.3 "Songti SC",serif}.plan-dialog-heading p{margin:0;color:#718095;font-size:12px}.plan-form{display:grid;gap:12px}.form-section{padding:18px 20px 4px;border:1px solid #e0e7ef;border-radius:15px;background:#f8fafc}.form-section>header{margin-bottom:16px;display:flex;align-items:center;gap:10px}.form-section>header>span{width:29px;height:29px;display:grid;place-items:center;border-radius:9px;background:#e9efff;color:#3157d5;font:700 9px "SFMono-Regular",monospace}.form-section>header>div{display:grid;gap:1px}.form-section>header strong{color:#24344b;font-size:13px}.form-section>header small{color:#8a97a7;font-size:9px}.plan-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.plan-form-grid--three{grid-template-columns:1fr 1fr 1fr}.plan-form :deep(.el-date-editor),.plan-form :deep(.el-select){width:100%}.plan-form :deep(.el-form-item){margin-bottom:15px}.plan-form :deep(.el-form-item__label){padding-bottom:7px;color:#607087;font-size:11px;font-weight:700}.plan-form :deep(.el-select__wrapper),.plan-form :deep(.el-input__wrapper){min-height:38px;border-radius:9px;background:#fff;box-shadow:0 0 0 1px #d9e2ec inset}.plan-form :deep(.el-select__wrapper.is-focused),.plan-form :deep(.el-input__wrapper.is-focus){box-shadow:0 0 0 1px #3157d5 inset,0 0 0 3px rgb(49 87 213/9%)}.prep-summary{margin:-1px 0 14px;padding:10px 12px;display:flex;align-items:baseline;gap:5px;border-radius:10px;background:#eaf0fc;color:#62748a;font-size:10px}.prep-summary strong{color:#3157d5;font:700 21px "Songti SC",serif}.prep-summary i{margin-left:auto;color:#8290a2;font-style:normal;font-size:9px}.plan-setup-dialog :deep(.el-dialog__footer){padding-top:14px;border-top:1px solid #e6ebf1}@media(max-width:680px){.form-section{padding:16px 15px 2px}.plan-form-grid,.plan-form-grid--three{grid-template-columns:1fr;gap:0}.prep-summary{align-items:flex-start;flex-wrap:wrap}.prep-summary i{width:100%;margin-left:0}.form-section>header small{display:none}}
</style>
