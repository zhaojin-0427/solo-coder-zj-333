import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'excerpts',
    component: () => import('@/pages/ExcerptPage.vue'),
    meta: { requiresAuth: true, title: '节目摘录' }
  },
  {
    path: '/topics',
    name: 'topics',
    component: () => import('@/pages/TopicsPage.vue'),
    meta: { requiresAuth: true, title: '专题整理' }
  },
  {
    path: '/family',
    name: 'family',
    component: () => import('@/pages/FamilyPage.vue'),
    meta: { requiresAuth: true, title: '家庭共享' }
  },
  {
    path: '/followups',
    name: 'followups',
    component: () => import('@/pages/FollowUpsPage.vue'),
    meta: { requiresAuth: true, title: '待跟进事项' }
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: () => import('@/pages/StatisticsPage.vue'),
    meta: { requiresAuth: true, title: '统计' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  userStore.initFromStorage()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
