<script setup>
import {
  Calendar,
  CreditCard,
  DataAnalysis,
  DocumentChecked,
  Expand,
  Fold,
  List,
  Medal,
} from '@element-plus/icons-vue'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { menuRoutes } from '../router/routes'
import { useUserStore } from '../store/userStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const iconMap = { Calendar, CreditCard, DataAnalysis, DocumentChecked, List, Medal }
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '训练台')

function logout() {
  userStore.logout()
  router.replace('/login')
}
</script>

<template>
  <el-container class="workspace-layout">
    <el-aside :width="collapsed ? '76px' : '238px'" class="workspace-aside">
      <RouterLink class="workspace-brand" to="/" :class="{ 'is-collapsed': collapsed }">
        <span class="brand__mark">准</span>
        <span v-show="!collapsed" class="workspace-brand__text">AI 考证教练</span>
      </RouterLink>

      <div v-show="!collapsed" class="aside-goal-label">学习工作台</div>

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        class="workspace-menu"
      >
        <el-menu-item v-for="item in menuRoutes" :key="item.name" :index="item.path ? `/${item.path}` : '/'">
          <el-icon><component :is="iconMap[item.meta.icon]" /></el-icon>
          <template #title>{{ item.meta.title }}</template>
        </el-menu-item>
      </el-menu>

      <div class="aside-upgrade" :class="{ 'is-collapsed': collapsed }">
        <template v-if="!collapsed">
          <span>解锁完整教练能力</span>
          <p>错因诊断、变式复测与掌握地图</p>
          <el-button type="primary" @click="router.push('/pricing')">查看套餐</el-button>
        </template>
        <el-icon v-else><CreditCard /></el-icon>
      </div>
    </el-aside>

    <el-container class="workspace-right">
      <el-header class="workspace-header">
        <div class="header-leading">
          <el-button class="collapse-button" text circle @click="collapsed = !collapsed">
            <el-icon :size="20"><Expand v-if="collapsed" /><Fold v-else /></el-icon>
          </el-button>
          <div>
            <span class="header-caption">AI EXAM COACH</span>
            <h1>{{ pageTitle }}</h1>
          </div>
        </div>

        <el-dropdown trigger="click">
          <button class="user-trigger">
            <span class="user-avatar">{{ userStore.nickname.slice(0, 1) }}</span>
            <span class="user-name">{{ userStore.nickname }}</span>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/pricing')">会员套餐</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="workspace-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>
