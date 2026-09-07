<script setup>
import { Search } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import CertificateCard from '../components/CertificateCard.vue'
import StudyPlanDrawer from '../components/StudyPlanDrawer.vue'
import StudyPlanSetupDialog from '../components/StudyPlanSetupDialog.vue'
import { generateStudyPlan, getCertificateCategories, getCertificates } from '../services/api'

const categories = ref([])
const certificates = ref([])
const total = ref(0)
const loading = ref(true)
const keyword = ref('')
const selectedCategory = ref('')
const selectedCertificate = ref(null)
const setupVisible = ref(false)
const planVisible = ref(false)
const generating = ref(false)
const generatedPlan = ref(null)
const errorMessage = ref('')

async function loadCertificates() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await getCertificates({ category: selectedCategory.value, keyword: keyword.value.trim(), page_size: 100 })
    certificates.value = result.items
    total.value = result.total
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

function openSetup(certificate) {
  errorMessage.value = ''
  selectedCertificate.value = certificate
  setupVisible.value = true
}

async function createPlan(form) {
  generating.value = true
  errorMessage.value = ''
  try {
    generatedPlan.value = await generateStudyPlan({ certificate_id: selectedCertificate.value.id, ...form })
    setupVisible.value = false
    planVisible.value = true
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  try {
    const [categoryData] = await Promise.all([getCertificateCategories(), loadCertificates()])
    categories.value = categoryData
  } catch (error) {
    errorMessage.value = error.message
  }
})
</script>

<template>
  <div class="certificate-square">
    <section class="square-hero">
      <div>
        <span class="square-kicker">找到你的下一张证书</span>
        <h2>先选方向，再把目标拆到今天。</h2>
        <p>覆盖计算机、财会、法律、工程、消防、教育、医药等主流职业资格与水平考试。</p>
      </div>
      <div class="square-count"><strong>{{ total }}</strong><span>项考试可规划</span></div>
    </section>

    <section class="square-toolbar">
      <el-input v-model="keyword" clearable placeholder="搜索证书、简称或组织机构" :prefix-icon="Search" class="certificate-search" @keyup.enter="loadCertificates" @clear="loadCertificates" />
      <div class="category-filter">
        <button :class="{ active: selectedCategory === '' }" @click="selectedCategory = ''; loadCertificates()">全部</button>
        <button v-for="category in categories" :key="category.code" :class="{ active: selectedCategory === category.code }" @click="selectedCategory = category.code; loadCertificates()">{{ category.name }}</button>
      </div>
    </section>

    <el-alert v-if="errorMessage && !setupVisible" :title="errorMessage" type="error" show-icon :closable="false" />
    <div v-loading="loading" class="certificate-grid">
      <CertificateCard v-for="certificate in certificates" :key="certificate.id" :certificate="certificate" @select="openSetup" />
    </div>
    <el-empty v-if="!loading && certificates.length === 0" description="没有找到匹配的证书" />

    <StudyPlanSetupDialog v-model="setupVisible" :certificate="selectedCertificate" :generating="generating" :error-message="errorMessage" @generate="createPlan" />
    <StudyPlanDrawer v-model="planVisible" :plan="generatedPlan" />
  </div>
</template>

<style scoped>
.certificate-square{width:min(1320px,100%);margin:0 auto}.square-hero{padding:42px 48px;display:flex;align-items:flex-end;justify-content:space-between;gap:30px;position:relative;overflow:hidden;border-radius:26px;background:#17233c;color:#fff}.square-hero:after{content:"证";position:absolute;right:155px;bottom:-85px;color:rgb(255 255 255/5%);font:700 300px/1 "Songti SC",serif}.square-kicker{color:#91a9ff;font:700 11px/1.4 "SFMono-Regular",monospace;letter-spacing:.14em}.square-hero h2{max-width:700px;margin:12px 0 13px;font:700 clamp(34px,4vw,54px)/1.15 "Songti SC",serif;letter-spacing:-.05em}.square-hero p{margin:0;color:#afbdd1;line-height:1.7}.square-count{min-width:150px;position:relative;z-index:1;text-align:right}.square-count strong{display:block;color:#ff9a7d;font:700 58px/1 "Songti SC",serif}.square-count span{color:#afbdd1;font-size:12px}.square-toolbar{margin:26px 0 22px;padding:18px;display:grid;gap:16px;border:1px solid #fff;border-radius:18px;background:rgb(248 251 254/82%)}.certificate-search{max-width:420px}.category-filter{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}.category-filter button{flex:none;padding:8px 13px;border:0;border-radius:9px;background:transparent;color:#62738a;font-size:12px;cursor:pointer}.category-filter button.active{background:#3157d5;color:#fff}.category-filter button:focus-visible{outline:3px solid rgb(49 87 213/24%);outline-offset:2px}.certificate-grid{min-height:300px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}@media(max-width:1050px){.certificate-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:680px){.square-hero{padding:30px 24px;align-items:flex-start;flex-direction:column}.square-count{text-align:left}.certificate-grid{grid-template-columns:1fr}}
.square-hero{min-height:188px;padding:28px 34px;align-items:center;border-radius:22px}.square-hero:after{bottom:-58px;font-size:220px}.square-kicker{font-size:10px}.square-hero h2{margin:9px 0 8px;font-size:clamp(30px,3.3vw,43px)}.square-hero p{font-size:13px}.square-count{min-width:120px}.square-count strong{font-size:44px}.square-count span{font-size:10px}.square-toolbar{margin:18px 0 20px;padding:15px;gap:13px;border-radius:16px}@media(max-width:680px){.square-hero{min-height:160px;padding:24px}}
</style>
