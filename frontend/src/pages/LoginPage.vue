<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-orange-100 py-12 px-4">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10">
        <div class="text-center mb-8">
          <div class="text-5xl mb-4">📻</div>
          <h1 class="text-3xl font-bold text-gray-800 mb-2">家庭电台助手</h1>
          <p class="text-lg text-gray-500">记录精彩节目，共享家庭温馨</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="w-full mt-4"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form>

        <div class="mt-8 pt-6 border-t border-gray-100">
          <p class="text-center text-gray-500 text-base mb-4">测试账号：</p>
          <div class="space-y-3">
            <div class="flex items-center justify-between bg-orange-50 rounded-lg px-4 py-3">
              <div class="flex items-center gap-3">
                <span class="text-2xl">👴</span>
                <div>
                  <p class="font-medium text-gray-800">张爷爷</p>
                  <p class="text-sm text-gray-500">grandpa / test123456</p>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-between bg-blue-50 rounded-lg px-4 py-3">
              <div class="flex items-center gap-3">
                <span class="text-2xl">👩</span>
                <div>
                  <p class="font-medium text-gray-800">张女儿</p>
                  <p class="text-sm text-gray-500">daughter / test123456</p>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-between bg-green-50 rounded-lg px-4 py-3">
              <div class="flex items-center gap-3">
                <span class="text-2xl">👨</span>
                <div>
                  <p class="font-medium text-gray-800">张儿子</p>
                  <p class="text-sm text-gray-500">son / test123456</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <p class="text-center text-gray-400 text-sm mt-6">
        © 2024 家庭电台助手 - 关爱长辈，记录美好
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功！')

        const redirect = route.query.redirect as string
        router.push(redirect || '/')
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>
