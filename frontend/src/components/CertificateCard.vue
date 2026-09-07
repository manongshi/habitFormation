<script setup>
import { ArrowRight, Calendar, Clock } from '@element-plus/icons-vue'

defineProps({
  certificate: { type: Object, required: true },
})

defineEmits(['select'])
</script>

<template>
  <article class="certificate-card">
    <button type="button" @click="$emit('select', certificate)">
      <div class="certificate-cover">
        <img :src="certificate.image_url" :alt="`${certificate.category.name}分类封面`" />
        <span v-if="certificate.is_featured" class="featured-badge">热门</span>
        <span class="category-badge">{{ certificate.category.name }}</span>
      </div>
      <div class="certificate-body">
        <div class="certificate-title-row">
          <div>
            <span v-if="certificate.short_name" class="certificate-short">{{ certificate.short_name }}</span>
            <h3>{{ certificate.name }}</h3>
          </div>
          <el-icon><ArrowRight /></el-icon>
        </div>
        <p>{{ certificate.issuer }}</p>
        <div class="certificate-meta">
          <span><el-icon><Calendar /></el-icon>建议 {{ certificate.recommended_days }} 天</span>
          <span><el-icon><Clock /></el-icon>{{ certificate.recommended_daily_minutes }} 分钟/天</span>
        </div>
        <div class="certificate-tags">
          <span>{{ certificate.exam_type }}</span>
          <span v-for="tag in certificate.tags.slice(0, 2)" :key="tag">{{ tag }}</span>
        </div>
      </div>
    </button>
  </article>
</template>

<style scoped>
.certificate-card{overflow:hidden;background:#f8fbfe;border:1px solid #fff;border-radius:20px;box-shadow:0 13px 38px rgb(37 61 92/8%);transition:transform .2s ease,box-shadow .2s ease}.certificate-card:hover{transform:translateY(-4px);box-shadow:0 22px 48px rgb(37 61 92/15%)}.certificate-card>button{width:100%;padding:0;display:block;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer}.certificate-card>button:focus-visible{outline:3px solid rgb(49 87 213/34%);outline-offset:-3px}.certificate-cover{height:154px;position:relative;overflow:hidden}.certificate-cover img{width:100%;height:100%;display:block;object-fit:cover}.featured-badge,.category-badge{position:absolute;top:13px;padding:5px 8px;border-radius:7px;font-size:10px;font-weight:700;backdrop-filter:blur(8px)}.featured-badge{left:13px;color:#8c321d;background:#ffd6ca}.category-badge{right:13px;color:#fff;background:rgb(17 28 49/55%)}.certificate-body{padding:20px}.certificate-title-row{min-height:62px;display:flex;align-items:flex-start;justify-content:space-between;gap:10px}.certificate-short{color:#3157d5;font-size:11px;font-weight:700}.certificate-body h3{margin:4px 0 0;font:700 17px/1.45 "Songti SC",serif}.certificate-body>p{height:36px;margin:10px 0 14px;color:#7a8798;font-size:11px;line-height:1.55}.certificate-meta{display:flex;gap:15px;color:#5c6e83;font-size:11px}.certificate-meta span{display:flex;align-items:center;gap:4px}.certificate-tags{margin-top:16px;display:flex;gap:6px;flex-wrap:wrap}.certificate-tags span{padding:5px 7px;color:#62738a;background:#e9f0f7;border-radius:6px;font-size:10px}@media(prefers-reduced-motion:reduce){.certificate-card{transition:none}}
</style>
