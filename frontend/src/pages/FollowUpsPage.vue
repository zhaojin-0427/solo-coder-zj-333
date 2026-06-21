<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📋</span>
      <span>待跟进事项</span>
      <el-button
        type="primary"
        size="large"
        class="ml-auto"
        @click="openAddDialog"
      >
        ➕ 新增事项
      </el-button>
    </h1>

    <div class="form-section mb-6">
      <div class="flex flex-wrap gap-3">
        <el-radio-group v-model="activeStatus" size="large" @change="loadFollowUps">
          <el-radio-button value="">
            📋 全部
            <el-tag size="large" class="ml-2">{{ allItems.length }}</el-tag>
          </el-radio-button>
          <el-radio-button value="pending">
            ⏳ 待处理
            <el-tag type="warning" size="large" class="ml-2">{{ pendingItems.length }}</el-tag>
          </el-radio-button>
          <el-radio-button value="in_progress">
            🔄 进行中
            <el-tag type="primary" size="large" class="ml-2">{{ inProgressItems.length }}</el-tag>
          </el-radio-button>
          <el-radio-button value="completed">
            ✅ 已完成
            <el-tag type="success" size="large" class="ml-2">{{ completedItems.length }}</el-tag>
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-loading text="加载中..." size="large" />
    </div>

    <div v-else-if="filteredItems.length === 0" class="loading-container">
      <el-empty description="暂无待跟进事项" />
    </div>

    <div v-else class="space-y-4">
      <el-card
        v-for="item in filteredItems"
        :key="item.id"
        class="shadow-card-hover"
        :body-style="{ padding: '20px' }"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <h3 class="text-xl font-semibold">{{ item.title }}</h3>
              <el-tag
                size="large"
                :class="`priority-${item.priority}`"
                effect="light"
              >
                {{ priorityText(item.priority) }}
              </el-tag>
              <el-tag
                size="large"
                :class="`status-${item.status}`"
                effect="light"
              >
                {{ statusText(item.status) }}
              </el-tag>
            </div>

            <p class="text-base text-gray-700 mb-3">{{ item.description }}</p>

            <div class="flex flex-wrap items-center gap-4 text-base text-gray-500">
              <span v-if="item.dueDate">
                📅 截止日期：{{ item.dueDate }}
              </span>
              <span>
                👤 负责人：{{ item.assignedTo?.avatar || '👤' }} {{ getUserName(item.assignedTo) }}
              </span>
              <span>
                📝 创建于：{{ formatTime(item.createdAt) }}
              </span>
            </div>

            <div
              v-if="item.excerpt"
              class="mt-4 p-4 bg-orange-50 rounded-xl border-l-4 border-primary"
            >
              <p class="text-sm text-gray-500 mb-1">关联节目：</p>
              <p class="text-base font-medium">📻 {{ item.excerpt.programName }}</p>
              <p class="text-sm text-gray-600 mt-1 line-clamp-2">{{ item.excerpt.contentSummary }}</p>
            </div>
          </div>

          <div class="flex flex-col gap-2 ml-6">
            <el-dropdown
              trigger="click"
              @command="(status: string) => updateStatus(item, status)"
            >
              <el-button size="large" type="primary">
                🔄 更改状态
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item value="pending">⏳ 待处理</el-dropdown-item>
                  <el-dropdown-item value="in_progress">🔄 进行中</el-dropdown-item>
                  <el-dropdown-item value="completed">✅ 已完成</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="addDialogVisible"
      title="➕ 新增待跟进事项"
      width="600px"
      size="large"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="事项标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入事项标题"
          />
        </el-form-item>

        <el-form-item label="事项描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入事项描述"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option label="🔴 高优先级" value="high" />
                <el-option label="🟡 中优先级" value="medium" />
                <el-option label="🟢 低优先级" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="assignedTo">
              <el-select v-model="formData.assignedTo" style="width: 100%">
                <el-option
                  v-for="member in members"
                  :key="member.id"
                  :label="`${member.avatar} ${member.firstName || member.username}`"
                  :value="member.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="⏳ 待处理" value="pending" />
                <el-option label="🔄 进行中" value="in_progress" />
                <el-option label="✅ 已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期" prop="dueDate">
              <el-date-picker
                v-model="formData.dueDate"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="关联节目（可选）" prop="excerptId">
          <el-select
            v-model="formData.excerptId"
            placeholder="选择关联的节目摘录"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option
              v-for="excerpt in excerpts"
              :key="excerpt.id"
              :label="`📻 ${excerpt.programName} - ${excerpt.date}`"
              :value="excerpt.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="addDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="handleSubmit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import type { FollowUpItem, FamilyMember, ProgramExcerpt, UserInfo } from '@/types'
import { followUpApi, familyApi, excerptApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const activeStatus = ref('')

const followUps = ref<FollowUpItem[]>([])
const members = ref<FamilyMember[]>([])
const excerpts = ref<ProgramExcerpt[]>([])

const userMap = reactive<Record<number, FamilyMember>>({})

const formRef = ref<FormInstance>()
const addDialogVisible = ref(false)

const today = new Date().toISOString().split('T')[0]

const formData = reactive({
  title: '',
  description: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  status: 'pending' as 'pending' | 'in_progress' | 'completed',
  assignedTo: null as number | null,
  dueDate: today,
  excerptId: null as number | null
})

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入事项标题', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入事项描述', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  assignedTo: [
    { required: true, message: '请选择负责人', trigger: 'change' }
  ]
}

const allItems = computed(() => followUps.value)
const pendingItems = computed(() => followUps.value.filter(i => i.status === 'pending'))
const inProgressItems = computed(() => followUps.value.filter(i => i.status === 'in_progress'))
const completedItems = computed(() => followUps.value.filter(i => i.status === 'completed'))

const filteredItems = computed(() => {
  if (!activeStatus.value) return followUps.value
  return followUps.value.filter(i => i.status === activeStatus.value)
})

const priorityText = (priority: string) => {
  const map: Record<string, string> = {
    high: '🔴 高优先级',
    medium: '🟡 中优先级',
    low: '🟢 低优先级'
  }
  return map[priority] || priority
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '⏳ 待处理',
    in_progress: '🔄 进行中',
    completed: '✅ 已完成'
  }
  return map[status] || status
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const getUserName = (assignedTo: UserInfo | null) => {
  if (!assignedTo) return '未分配'
  return assignedTo.firstName || assignedTo.username || '未知用户'
}

const loadFollowUps = async () => {
  loading.value = true
  try {
    followUps.value = await followUpApi.getList()
  } catch (error) {
    console.error('Failed to load follow-ups:', error)
  } finally {
    loading.value = false
  }
}

const loadMembers = async () => {
  try {
    members.value = await familyApi.getMembers()
    members.value.forEach(member => {
      userMap[member.id] = member
    })
  } catch (error) {
    console.error('Failed to load members:', error)
  }
}

const loadExcerpts = async () => {
  try {
    excerpts.value = await excerptApi.getList()
  } catch (error) {
    console.error('Failed to load excerpts:', error)
  }
}

const openAddDialog = () => {
  formData.title = ''
  formData.description = ''
  formData.priority = 'medium'
  formData.status = 'pending'
  formData.assignedTo = members.value[0]?.id || null
  formData.dueDate = today
  formData.excerptId = null
  addDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await followUpApi.create({
          title: formData.title,
          description: formData.description,
          priority: formData.priority,
          status: formData.status,
          assignedToId: formData.assignedTo,
          dueDate: formData.dueDate,
          excerptId: formData.excerptId
        })
        ElMessage.success('创建成功！')
        addDialogVisible.value = false
        loadFollowUps()
      } catch (error) {
        console.error('Submit error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const updateStatus = async (item: FollowUpItem, status: string) => {
  try {
    await followUpApi.updateStatus(item.id, status)
    ElMessage.success(`状态已更新为「${statusText(status)}」`)
    loadFollowUps()
  } catch (error) {
    console.error('Update status error:', error)
  }
}

onMounted(() => {
  loadMembers()
  loadExcerpts()
  loadFollowUps()
})
</script>
