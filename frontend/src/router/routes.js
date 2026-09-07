import AppLayout from '../layouts/AppLayout.vue'

export const publicRoutes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/AuthView.vue'),
    props: { mode: 'login' },
    meta: { title: '登录', public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/AuthView.vue'),
    props: { mode: 'register' },
    meta: { title: '注册', public: true },
  },
]

export const appRoute = {
  path: '/',
  component: AppLayout,
  redirect: '/certificates',
  meta: { requiresAuth: true },
  children: [
    {
      path: 'todos',
      name: 'todos',
      component: () => import('../views/TodoView.vue'),
      meta: {
        title: '我的代办',
        icon: 'List',
        menu: true,
        permission: 'todos:view',
      },
    },
    {
      path: 'certificates',
      name: 'certificates',
      component: () => import('../views/CertificateSquareView.vue'),
      meta: {
        title: '证书广场',
        icon: 'Medal',
        menu: true,
        permission: 'certificates:view',
      },
    },
    {
      path: 'today',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        title: '今日训练',
        icon: 'Calendar',
        menu: true,
        permission: 'dashboard:view',
      },
    },
    {
      path: 'mastery',
      name: 'mastery',
      component: () => import('../views/PlaceholderView.vue'),
      props: { title: '掌握地图', description: '后续可在这里查看各知识点的学习进度。' },
      meta: {
        title: '掌握地图',
        icon: 'DataAnalysis',
        menu: true,
        permission: 'mastery:view',
      },
    },
    {
      path: 'mistakes',
      name: 'mistakes',
      component: () => import('../views/PlaceholderView.vue'),
      props: { title: '错题复测', description: '后续可在这里集中整理和回顾错题。' },
      meta: {
        title: '错题复测',
        icon: 'DocumentChecked',
        menu: true,
        permission: 'mistakes:view',
      },
    },
    {
      path: 'pricing',
      name: 'pricing',
      component: () => import('../views/PricingView.vue'),
      meta: {
        title: '会员套餐',
        icon: 'CreditCard',
        menu: true,
        permission: 'subscription:view',
      },
    },
  ],
}

export const routes = [...publicRoutes, appRoute]

export const menuRoutes = appRoute.children.filter((route) => route.meta?.menu)
