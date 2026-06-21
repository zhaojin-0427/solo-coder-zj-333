<template>
  <div class="page-container">
    <div class="flex items-center gap-3 mb-6">
      <el-button size="large" @click="router.back()">
        ← 返回
      </el-button>
      <h1 class="page-title mb-0">
        <span>📚</span>
        <span>资料包详情</span>
      </h1>
    </div>

    <div v-if="loading" class="loading-container py-16">
      <div class="text-gray-500 text-lg">⏳ 加载中...</div>
    </div>

    <div v-else-if="!packageData" class="loading-container py-16">
      <el-empty description="资料包不存在" />
    </div>

    <template v-else>
      <el-card class="shadow-card mb-6" :body-style="{ padding: '24px' }">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h2 class="text-2xl font-bold mb-2">{{ packageData.title }}</h2>
            <p class="text-sm text-gray-500 mb-3">
              创建人：{{ packageData.createdByName }} · 创建于 {{ formatDate(packageData.createdAt) }}
            </p>

            <div v-if="packageData.purposeDescription" class="mb-3">
              <span class="text-sm text-gray-500">📌 用途说明：</span>
              <span class="text-base text-gray-700">{{ packageData.purposeDescription }}</span>
            </div>

            <div v-if="packageData.guideText" class="p-4 bg-orange-50 rounded-lg">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-lg">💬</span>
                <span class="font-semibold text-primary">导览语</span>
              </div>
              <p class="text-base text-gray-700">{{ packageData.guideText }}</p>
            </div>
          </div>

          <div v-if="isFamily" class="flex flex-col gap-2">
            <el-button type="primary" size="large" @click="openEditDialog">
              ✏️ 编辑资料包
            </el-button>
          </div>
        </div>
      </el-card>

      <h3 class="text-xl font-semibold mb-4">
        📄 内容列表
        <span class="text-sm text-gray-500 font-normal ml-2">（共 {{ packageData.items?.length || 0 }} 条）</span>
      </h3>

      <div v-if="!packageData.items || packageData.items.length === 0" class="mb-6">
        <el-empty description="资料包暂无内容" />
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="(item, index) in sortedItems"
          :key="item.id"
          class="relative"
        >
          <el-card
            class="shadow-card-hover"
            :body-style="{ padding: '20px' }"
            :class="{ 'border-2 border-yellow-400': item.isHighlighted }"
          >
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center text-lg font-bold">
                {{ index + 1 }}
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2 flex-wrap">
                  <span class="text-lg font-semibold">📻 {{ item.excerpt?.programName }}</span>
                  <span class="text-sm text-gray-500">📅 {{ item.excerpt?.date }}</span>
                  <el-tag
                    v-if="item.excerpt?.topic"
                    :style="{ backgroundColor: item.excerpt.topic.color + '20', color: item.excerpt.topic.color }"
                    size="large"
                  >
                    {{ item.excerpt.topic.icon }} {{ item.excerpt.topic.name }}
                  </el-tag>
                  <el-tag
                    :type="confirmationTagType(item.excerpt?.confirmationStatus)"
                    size="large"
                    effect="light"
                  >
                    {{ confirmationLabel(item.excerpt?.confirmationStatus) }}
                  </el-tag>
                  <el-tag
                    v-if="item.isHighlighted"
                    type="warning"
                    size="large"
                    effect="dark"
                  >
                    ⭐ 重点
                  </el-tag>
                </div>

                <div class="text-base text-gray-700 mb-3">
                  <span class="font-medium">📝 内容摘要：</span>
                  {{ item.excerpt?.contentSummary }}
                </div>

                <div
                  v-if="item.excerpt?.elderlyNotes"
                  class="bg-elderly rounded-lg p-3 mb-3"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-lg">👴</span>
                    <span class="font-semibold text-primary">老人补充</span>
                  </div>
                  <p class="text-base text-gray-800">{{ item.excerpt.elderlyNotes }}</p>
                </div>

                <div
                  v-if="item.familyReminder"
                  class="p-3 rounded-lg bg-blue-50 border-l-4 border-blue-400 mb-3"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-lg">👨‍👩‍👧</span>
                    <span class="font-semibold text-blue-700">家属提醒</span>
                  </div>
                  <p class="text-base text-gray-700">{{ item.familyReminder }}</p>
                </div>

                <div v-if="item.latestFeedback" class="p-3 rounded-lg bg-green-50 border-l-4 border-green-400">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-lg">{{ feedbackIcon(item.latestFeedback.feedbackType) }}</span>
                    <span class="font-semibold text-green-700">
                      {{ item.latestFeedback.feedbackTypeDisplay }}
                    </span>
                    <span class="text-sm text-gray-500">
                      · {{ item.latestFeedback.elderlyUserName }} · {{ formatDateTime(item.latestFeedback.createdAt) }}
                    </span>
                  </div>
                  <p v-if="item.latestFeedback.note" class="text-sm text-gray-600">
                    {{ item.latestFeedback.note }}
                  </p>
                </div>

                <div v-if="isElderly" class="mt-4 pt-4 border-t border-gray-100">
                  <p class="text-base text-gray-600 mb-3">请选择您的反馈：</p>
                  <div class="flex flex-wrap gap-3">
                    <el-button
                      size="large"
                      :type="item.feedbackType === 'read' ? 'success' : 'default'"
                      @click="submitFeedback(item, 'read')"
                    >
                      ✅ 已读
                    </el-button>
                    <el-button
                      size="large"
                      :type="item.feedbackType === 'review_again' ? 'warning' : 'default'"
                      @click="submitFeedback(item, 'review_again')"
                    >
                      🔄 还想再看
                    </el-button>
                    <el-button
                      size="large"
                      :type="item.feedbackType === 'needs_explanation' ? 'danger' : 'default'"
                      @click="openFeedbackDialog(item)"
                    >
                      ❓ 需要家人讲解
                    </el-button>
                  </div>
                </div>

                <div v-if="isFamily" class="mt-4 pt-4 border-t border-gray-100 flex flex-wrap gap-3">
                  <el-button
                    size="large"
                    :type="item.isHighlighted ? 'warning' : 'default'"
                    @click="toggleHighlight(item)"
                  >
                    {{ item.isHighlighted ? '⭐ 取消重点' : '⭐ 标记重点' }}
                  </el-button>
                  <el-button size="large" @click="openReminderDialog(item)">
                    💬 {{ item.familyReminder ? '编辑提醒' : '添加提醒' }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </template>

    <el-dialog
      v-model="feedbackDialogVisible"
      title="❓ 需要家人讲解"
      width="500px"
      size="large"
    >
      <el-form label-position="top" size="large">
        <el-form-item label="补充说明（可选）">
          <el-input
            v-model="feedbackNote"
            type="textarea"
            :rows="3"
            placeholder="可以告诉家人您哪里不明白..."
          />
        </el-form-item>
      </el-form>

      <div class="p-4 bg-orange-50 rounded-lg">
        <p class="text-sm text-orange-700">
          💡 提交后将自动生成一条待跟进事项，通知家人来为您讲解。
        </p>
      </div>

      <template #footer>
        <el-button size="large" @click="feedbackDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="danger"
          size="large"
          :loading="submittingFeedback"
          @click="confirmNeedsExplanation"
        >
          提交并通知家人
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="reminderDialogVisible"
      title="💬 家属提醒"
      width="500px"
      size="large"
    >
      <el-form label-position="top" size="large">
        <el-form-item label="提醒内容">
          <el-input
            v-model="reminderText"
            type="textarea"
            :rows="3"
            placeholder="输入给老人的提醒内容..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="reminderDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submittingReminder"
          @click="saveReminder"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="editDialogVisible"
      title="✏️ 编辑资料包"
      width="800px"
      size="large"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editFormData"
        :rules="editFormRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="资料包标题" prop="title">
          <el-input v-model="editFormData.title" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="用途说明">
              <el-input
                v-model="editFormData.purposeDescription"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="导览语">
              <el-input
                v-model="editFormData.guideText"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="选择节目摘录（1-20条）" prop="excerptIds">
          <div class="excerpt-selector">
            <div class="flex items-center justify-between mb-3">
              <span class="text-base text-gray-600">
                已选择 <span class="font-bold text-primary">{{ editFormData.excerptIds.length }}</span> / 20 条
              </span>
            </div>

            <div class="excerpt-list max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
              <div
                v-for="excerpt in availableExcerpts"
                :key="excerpt.id"
                class="excerpt-item flex items-start gap-3 p-3 border-b border-gray-100 hover:bg-orange-50 transition-colors"
                :class="{ 'bg-orange-50': editFormData.excerptIds.includes(excerpt.id) }"
              >
                <el-checkbox
                  :model-value="editFormData.excerptIds.includes(excerpt.id)"
                  @change="(val: boolean) => toggleEditExcerpt(excerpt.id, val)"
                />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold">📻 {{ excerpt.programName }}</span>
                    <span class="text-sm text-gray-500">📅 {{ excerpt.date }}</span>
                  </div>
                  <p class="text-sm text-gray-600 line-clamp-1">{{ excerpt.contentSummary }}</p>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="editDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submittingEdit"
          @click="handleEdit"
        >
          保存修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { ReviewPackage, ReviewPackageItem, ProgramExcerpt } from '@/types'
import { reviewPackageApi, excerptApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submittingFeedback = ref(false)
const submittingReminder = ref(false)
const submittingEdit = ref(false)

const packageData = ref<ReviewPackage | null>(null)
const availableExcerpts = ref<ProgramExcerpt[]>([])

const feedbackDialogVisible = ref(false)
const feedbackNote = ref('')
const currentFeedbackItem = ref<ReviewPackageItem | null>(null)

const reminderDialogVisible = ref(false)
const reminderText = ref('')
const currentReminderItem = ref<ReviewPackageItem | null>(null)

const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editFormData = reactive({
  title: '',
  purposeDescription: '',
  guideText: '',
  excerptIds: [] as number[]
})

const editFormRules: FormRules = {
  title: [
    { required: true, message: '请输入资料包标题', trigger: 'blur' }
  ],
  excerptIds: [
    {
      validator: (_rule, value, callback) => {
        if (value.length === 0) {
          callback(new Error('请至少选择一条节目摘录'))
        } else if (value.length > 20) {
          callback(new Error('最多只能选择 20 条'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const isElderly = computed(() => userStore.user?.role === 'elderly')
const isFamily = computed(() => userStore.user?.role === 'family' || userStore.user?.role === 'admin')

const sortedItems = computed(() => {
  if (!packageData.value?.items) return []
  return [...packageData.value.items].sort((a, b) => a.orderIndex - b.orderIndex)
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const confirmationTagType = (status?: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    confirmed: 'success',
    needs_verification: 'danger'
  }
  return map[status || ''] || 'info'
}

const confirmationLabel = (status?: string) => {
  const map: Record<string, string> = {
    pending: '⏳ 待确认',
    confirmed: '✅ 已确认',
    needs_verification: '❗ 需核实'
  }
  return map[status || ''] || status
}

const feedbackIcon = (type: string) => {
  const map: Record<string, string> = {
    read: '✅',
    review_again: '🔄',
    needs_explanation: '❓'
  }
  return map[type] || '📝'
}

const loadPackage = async () => {
  const id = Number(route.params.id)
  if (!id) return

  loading.value = true
  try {
    packageData.value = await reviewPackageApi.getDetail(id)
  } catch (error) {
    console.error('Failed to load package:', error)
  } finally {
    loading.value = false
  }
}

const loadExcerpts = async () => {
  try {
    availableExcerpts.value = await excerptApi.getList()
  } catch (error) {
    console.error('Failed to load excerpts:', error)
  }
}

const submitFeedback = async (item: ReviewPackageItem, type: 'read' | 'review_again' | 'needs_explanation') => {
  if (type === 'needs_explanation') {
    openFeedbackDialog(item)
    return
  }

  try {
    await reviewPackageApi.submitFeedback(item.id, type)
    ElMessage.success('反馈已提交！')
    loadPackage()
  } catch (error) {
    console.error('Submit feedback error:', error)
  }
}

const openFeedbackDialog = (item: ReviewPackageItem) => {
  currentFeedbackItem.value = item
  feedbackNote.value = ''
  feedbackDialogVisible.value = true
}

const confirmNeedsExplanation = async () => {
  if (!currentFeedbackItem.value) return

  submittingFeedback.value = true
  try {
    const result = await reviewPackageApi.submitFeedback(
      currentFeedbackItem.value.id,
      'needs_explanation',
      feedbackNote.value
    )
    ElMessage.success('已通知家人，他们会尽快为您讲解！')
    if (result.generatedFollowup) {
      ElMessage.info('已生成待跟进事项')
    }
    feedbackDialogVisible.value = false
    loadPackage()
  } catch (error) {
    console.error('Submit feedback error:', error)
  } finally {
    submittingFeedback.value = false
  }
}

const toggleHighlight = async (item: ReviewPackageItem) => {
  try {
    await reviewPackageApi.updateItemConfig(item.id, {
      isHighlighted: !item.isHighlighted
    })
    ElMessage.success(item.isHighlighted ? '已取消重点标记' : '已标记为重点')
    loadPackage()
  } catch (error) {
    console.error('Toggle highlight error:', error)
  }
}

const openReminderDialog = (item: ReviewPackageItem) => {
  currentReminderItem.value = item
  reminderText.value = item.familyReminder || ''
  reminderDialogVisible.value = true
}

const saveReminder = async () => {
  if (!currentReminderItem.value) return

  submittingReminder.value = true
  try {
    await reviewPackageApi.updateItemConfig(currentReminderItem.value.id, {
      familyReminder: reminderText.value || null
    })
    ElMessage.success('提醒已保存！')
    reminderDialogVisible.value = false
    loadPackage()
  } catch (error) {
    console.error('Save reminder error:', error)
  } finally {
    submittingReminder.value = false
  }
}

const openEditDialog = async () => {
  if (!packageData.value) return

  editFormData.title = packageData.value.title
  editFormData.purposeDescription = packageData.value.purposeDescription || ''
  editFormData.guideText = packageData.value.guideText || ''
  editFormData.excerptIds = packageData.value.items?.map(i => i.excerpt?.id!).filter(Boolean) || []

  await loadExcerpts()
  editDialogVisible.value = true
}

const toggleEditExcerpt = (excerptId: number, selected: boolean) => {
  if (selected) {
    if (editFormData.excerptIds.length >= 20) {
      ElMessage.warning('最多只能选择 20 条')
      return
    }
    editFormData.excerptIds.push(excerptId)
  } else {
    editFormData.excerptIds = editFormData.excerptIds.filter(id => id !== excerptId)
  }
}

const handleEdit = async () => {
  if (!editFormRef.value || !packageData.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submittingEdit.value = true
      try {
        await reviewPackageApi.update(packageData.value.id, {
          title: editFormData.title,
          purposeDescription: editFormData.purposeDescription || null,
          guideText: editFormData.guideText || null,
          excerptIds: editFormData.excerptIds
        })
        ElMessage.success('资料包已更新！')
        editDialogVisible.value = false
        loadPackage()
      } catch (error) {
        console.error('Edit package error:', error)
      } finally {
        submittingEdit.value = false
      }
    }
  })
}

onMounted(() => {
  loadPackage()
})
</script>
