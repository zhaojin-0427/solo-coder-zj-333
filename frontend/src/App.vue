<template>
  <div class="min-h-screen bg-bg">
    <template v-if="userStore.isLoggedIn">
      <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
              <span class="text-3xl">📻</span>
              <h1 class="text-2xl font-bold text-primary">家庭电台助手</h1>
            </div>

            <nav class="hidden md:flex items-center gap-2">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="nav-item"
                :class="{ active: route.path === item.path }"
              >
                <span class="text-xl">{{ item.icon }}</span>
                <span>{{ item.title }}</span>
              </router-link>
            </nav>

            <div class="flex items-center gap-4">
              <el-dropdown trigger="click" @command="handleUserCommand">
                <div class="flex items-center gap-3 cursor-pointer hover:bg-orange-50 px-3 py-2 rounded-lg transition-colors">
                  <span class="text-2xl">{{ userStore.user?.avatar || '👤' }}</span>
                  <span class="text-lg font-medium hidden sm:inline">{{ userStore.user?.firstName || userStore.user?.username || '用户' }}</span>
                  <el-icon class="text-gray-400"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item disabled>
                      <span class="flex items-center gap-2">
                        <span>{{ userStore.user?.avatar }}</span>
                        <span>{{ userStore.user?.firstName || userStore.user?.username }}</span>
                      </span>
                    </el-dropdown-item>
                    <el-dropdown-item disabled class="text-sm text-gray-500">
                      {{ userStore.user?.role === 'elderly' ? '长辈' : userStore.user?.role === 'admin' ? '管理员' : '家人' }}
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      🚪 退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <div class="md:hidden border-t border-gray-100">
          <div class="flex overflow-x-auto py-2 px-2 gap-1">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="flex-shrink-0 flex items-center gap-1 px-4 py-2 rounded-lg text-base whitespace-nowrap transition-colors"
              :class="route.path === item.path ? 'bg-primary text-white' : 'text-gray-600 hover:bg-orange-50'"
            >
              <span class="text-lg">{{ item.icon }}</span>
              <span>{{ item.title }}</span>
            </router-link>
          </div>
        </div>
      </header>

      <main class="transition-all duration-300">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </template>

    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const navItems = [
  { path: '/', title: '节目摘录', icon: '📻' },
  { path: '/topics', title: '专题整理', icon: '📁' },
  { path: '/review-packages', title: '回听资料包', icon: '📚' },
  { path: '/companion-plans', title: '陪办计划', icon: '🤝' },
  { path: '/family', title: '家庭共享', icon: '👨‍👩‍👧‍👦' },
  { path: '/followups', title: '待跟进', icon: '📋' },
  { path: '/statistics', title: '统计', icon: '📊' }
]

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '退出确认',
        {
          confirmButtonText: '确定退出',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Logout error:', error)
      }
    }
  }
}
</script>
