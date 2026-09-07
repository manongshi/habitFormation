import { createRouter, createWebHistory } from 'vue-router'

import pinia from '../store'
import { useUserStore } from '../store/userStore'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const userStore = useUserStore(pinia)

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.public && userStore.isLoggedIn) {
    return { name: 'certificates' }
  }

  if (userStore.isLoggedIn && !userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      userStore.logout()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  document.title = `${to.meta.title || '训练台'} - AI 考证教练`
  return true
})

export default router
