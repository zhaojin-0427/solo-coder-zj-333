<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📻</span>
      <span>节目摘录</span>
      <el-tag type="success" size="large" class="ml-2">
        共 {{ excerpts.length }} 条记录
      </el-tag>
    </h1>

    <el-row :gutter="24">
      <el-col :xs="24" :lg="8">
        <div class="form-section">
          <h2 class="section-title">✏️ 录入节目</h2>
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-position="top"
            size="large"
          >
            <el-form-item label="收听日期" prop="date">
              <el-date-picker
                v-model="formData.date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :disabled-date="disabledDate"
              />
            </el-form-item>

            <el-form-item label="节目名称" prop="programName">
              <el-input
                v-model="formData.programName"
                placeholder="请输入节目名称"
              />
            </el-form-item>

            <el-form-item label="播出时段" prop="timeSlot">
              <el-select v-model="formData.timeSlot" placeholder="选择时段" style="width: 100%">
                <el-option label="早晨 06:00-09:00" value="早晨 06:00-09:00" />
                <el-option label="上午 09:00-12:00" value="上午 09:00-12:00" />
                <el-option label="中午 12:00-14:00" value="中午 12:00-14:00" />
                <el-option label="下午 14:00-18:00" value="下午 14:00-18:00" />
                <el-option label="傍晚 18:00-20:00" value="傍晚 18:00-20:00" />
                <el-option label="晚间 20:00-22:00" value="晚间 20:00-22:00" />
              </el-select>
            </el-form-item>

            <el-form-item label="内容摘要" prop="contentSummary">
              <el-input
                v-model="formData.contentSummary"
                type="textarea"
                :rows="4"
                placeholder="请输入节目内容摘要"
              />
            </el-form-item>

            <el-form-item label="所属专题" prop="topicId">
              <el-select
                v-model="formData.topicId"
                placeholder="选择专题（可选）"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="topic in topics"
                  :key="topic.id"
                  :label="`${topic.icon} ${topic.name}`"
                  :value="topic.id"
                />
              </el-select>
            </el-form-item>

            <div class="elderly-section">
              <h3 class="section-title">👴 老人补充区</h3>
              <el-form-item label="老人的话" prop="elderlyNotes">
                <el-input
                  v-model="formData.elderlyNotes"
                  type="textarea"
                  :rows="3"
                  placeholder="记录老人想说的话、感受或补充内容"
                />
              </el-form-item>
            </div>

            <el-button
              type="primary"
              size="large"
              class="w-full"
              :loading="submitting"
              @click="handleSubmit"
            >
              {{ editingId ? '保存修改' : '保存摘录' }}
            </el-button>

            <el-button
              v-if="editingId"
              size="large"
              class="w-full mt-3"
              @click="resetForm"
            >
              取消编辑
            </el-button>
          </el-form>
        </div>

        <div class="form-section">
          <h2 class="section-title">🔍 筛选条件</h2>
          <el-form label-position="top" size="large">
            <el-form-item label="按日期筛选">
              <el-date-picker
                v-model="filterDate"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                clearable
                @change="loadExcerpts"
              />
            </el-form-item>

            <el-form-item label="按专题筛选">
              <el-select
                v-model="filterTopicId"
                placeholder="选择专题"
                style="width: 100%"
                clearable
                @change="loadExcerpts"
              >
                <el-option
                  v-for="topic in topics"
                  :key="topic.id"
                  :label="`${topic.icon} ${topic.name}`"
                  :value="topic.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="确认状态筛选">
              <el-select
                v-model="filterConfirmationStatus"
                placeholder="全部状态"
                style="width: 100%"
                clearable
                @change="loadExcerpts"
              >
                <el-option label="⏳ 待确认" value="pending" />
                <el-option label="✅ 已确认" value="confirmed" />
                <el-option label="❗ 需核实" value="needs_verification" />
              </el-select>
            </el-form-item>

            <el-form-item label="包含重复记录">
              <el-switch
                v-model="includeDuplicates"
                size="large"
                active-text="显示"
                inactive-text="隐藏"
                @change="loadExcerpts"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :xs="24" :lg="16">
        <div v-if="loading" class="loading-container">
          <el-loading text="加载中..." size="large" />
        </div>

        <div v-else-if="excerpts.length === 0" class="loading-container">
          <el-empty description="暂无记录，快去录入第一条节目吧！" />
        </div>

        <div v-else class="card-grid">
          <el-card
            v-for="excerpt in excerpts"
            :key="excerpt.id"
            class="shadow-card-hover"
            :body-style="{ padding: '20px' }"
          >
            <template #header>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="text-2xl">📻</span>
                  <span class="text-xl font-semibold">{{ excerpt.programName }}</span>
                  <span
                    v-if="excerpt.isDuplicate"
                    class="duplicate-badge"
                  >
                    ⚠️ 重复记录
                  </span>
                  <el-tag
                    :type="confirmationTagType(excerpt.confirmationStatus)"
                    size="large"
                    effect="light"
                  >
                    {{ confirmationLabel(excerpt.confirmationStatus) }}
                  </el-tag>
                </div>
                <el-tag
                  v-if="excerpt.topic"
                  :style="{ backgroundColor: excerpt.topic.color + '20', color: excerpt.topic.color, borderColor: excerpt.topic.color }"
                  effect="light"
                >
                  {{ excerpt.topic.icon }} {{ excerpt.topic.name }}
                </el-tag>
              </div>
            </template>

            <div class="space-y-3">
              <div class="flex items-center gap-4 text-base text-gray-600">
                <span>📅 {{ excerpt.date }}</span>
                <span>⏰ {{ excerpt.timeSlot }}</span>
              </div>

              <div class="text-base">
                <span class="font-medium text-gray-800">内容摘要：</span>
                <span class="text-gray-700">{{ excerpt.contentSummary }}</span>
              </div>

              <div
                v-if="excerpt.elderlyNotes"
                class="bg-elderly rounded-lg p-4 mt-4"
              >
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-xl">👴</span>
                  <span class="font-semibold text-primary">老人补充</span>
                </div>
                <p class="text-lg text-gray-800 leading-relaxed">{{ excerpt.elderlyNotes }}</p>
              </div>

              <div
                v-if="excerpt.confirmationStatus !== 'pending' && excerpt.confirmedByName"
                class="p-3 rounded-lg border-l-4"
                :class="excerpt.confirmationStatus === 'confirmed' ? 'bg-green-50 border-green-400' : 'bg-orange-50 border-orange-400'"
              >
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-sm">
                    {{ excerpt.confirmationStatus === 'confirmed' ? '✅ 已确认' : '❗ 需核实' }}
                  </span>
                  <span class="text-sm text-gray-500">
                    由 {{ excerpt.confirmedByName }} 确认于 {{ formatTime(excerpt.confirmedAt!) }}
                  </span>
                </div>
                <p v-if="excerpt.confirmationNote" class="text-sm text-gray-600">
                  备注：{{ excerpt.confirmationNote }}
                </p>
              </div>

              <el-divider class="my-4" />

              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  创建于 {{ formatTime(excerpt.createdAt) }}
                </div>
                <div class="flex gap-2">
                  <el-button
                    v-if="excerpt.confirmationStatus === 'pending'"
                    type="success"
                    size="large"
                    @click="openConfirmDialog(excerpt, 'confirmed')"
                  >
                    ✅ 确认
                  </el-button>
                  <el-button
                    v-if="excerpt.confirmationStatus === 'pending'"
                    type="warning"
                    size="large"
                    @click="openConfirmDialog(excerpt, 'needs_verification')"
                  >
                    ❗ 需核实
                  </el-button>
                  <el-button size="large" @click="handleEdit(excerpt)">
                    ✏️ 编辑
                  </el-button>
                  <el-button
                    size="large"
                    type="danger"
                    :loading="deletingId === excerpt.id"
                    @click="handleDelete(excerpt)"
                  >
                    🗑️ 删除
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <el-dialog
      v-model="confirmDialogVisible"
      :title="confirmAction === 'confirmed' ? '✅ 确认摘录' : '❗ 标记需核实'"
      width="500px"
      size="large"
    >
      <div class="space-y-4">
        <div v-if="confirmingExcerpt" class="p-4 bg-orange-50 rounded-xl">
          <p class="font-semibold text-lg">{{ confirmingExcerpt.programName }}</p>
          <p class="text-sm text-gray-500 mt-1 line-clamp-2">{{ confirmingExcerpt.contentSummary }}</p>
        </div>

        <el-form label-position="top" size="large">
          <el-form-item :label="confirmAction === 'confirmed' ? '确认备注（可选）' : '核实备注（必填）'">
            <el-input
              v-model="confirmNote"
              type="textarea"
              :rows="3"
              :placeholder="confirmAction === 'confirmed' ? '可填写确认备注...' : '请填写需要核实的原因或说明...'"
            />
          </el-form-item>
        </el-form>

        <el-checkbox
          v-if="confirmAction === 'needs_verification'"
          v-model="generateFollowup"
        >
          一键生成关联待跟进事项
        </el-checkbox>
      </div>

      <template #footer>
        <el-button size="large" @click="confirmDialogVisible = false">
          取消
        </el-button>
        <el-button
          :type="confirmAction === 'confirmed' ? 'success' : 'warning'"
          size="large"
          :loading="confirming"
          :disabled="confirmAction === 'needs_verification' && !confirmNote.trim()"
          @click="handleConfirm"
        >
          {{ confirmAction === 'confirmed' ? '确认' : '标记需核实' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { ProgramExcerpt, Topic } from '@/types'
import { excerptApi, topicApi } from '@/api'

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const deletingId = ref<number | null>(null)
const editingId = ref<number | null>(null)

const excerpts = ref<ProgramExcerpt[]>([])
const topics = ref<Topic[]>([])

const filterDate = ref<string>('')
const filterTopicId = ref<number | null>(null)
const filterConfirmationStatus = ref<string>('')
const includeDuplicates = ref(false)

const confirmDialogVisible = ref(false)
const confirmingExcerpt = ref<ProgramExcerpt | null>(null)
const confirmAction = ref<'confirmed' | 'needs_verification'>('confirmed')
const confirmNote = ref('')
const generateFollowup = ref(true)
const confirming = ref(false)

const today = new Date().toISOString().split('T')[0]

const formData = reactive({
  date: today,
  programName: '',
  timeSlot: '',
  contentSummary: '',
  elderlyNotes: '',
  topicId: null as number | null
})

const formRules: FormRules = {
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  programName: [
    { required: true, message: '请输入节目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  timeSlot: [
    { required: true, message: '请选择播出时段', trigger: 'change' }
  ],
  contentSummary: [
    { required: true, message: '请输入内容摘要', trigger: 'blur' },
    { min: 5, max: 2000, message: '长度在 5 到 2000 个字符', trigger: 'blur' }
  ]
}

const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const formatTime = (timeStr: string | null) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const confirmationTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    confirmed: 'success',
    needs_verification: 'danger'
  }
  return map[status] || 'info'
}

const confirmationLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '⏳ 待确认',
    confirmed: '✅ 已确认',
    needs_verification: '❗ 需核实'
  }
  return map[status] || status
}

const loadTopics = async () => {
  try {
    topics.value = await topicApi.getList()
  } catch (error) {
    console.error('Failed to load topics:', error)
  }
}

const loadExcerpts = async () => {
  loading.value = true
  try {
    excerpts.value = await excerptApi.getList({
      date: filterDate.value || undefined,
      topicId: filterTopicId.value || undefined,
      includeDuplicates: includeDuplicates.value,
      confirmationStatus: filterConfirmationStatus.value || undefined
    })
  } catch (error) {
    console.error('Failed to load excerpts:', error)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingId.value) {
          await excerptApi.update(editingId.value, formData)
          ElMessage.success('修改成功！')
        } else {
          await excerptApi.create(formData)
          ElMessage.success('保存成功！')
        }
        resetForm()
        loadExcerpts()
      } catch (error) {
        console.error('Submit error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleEdit = (excerpt: ProgramExcerpt) => {
  editingId.value = excerpt.id
  formData.date = excerpt.date
  formData.programName = excerpt.programName
  formData.timeSlot = excerpt.timeSlot
  formData.contentSummary = excerpt.contentSummary
  formData.elderlyNotes = excerpt.elderlyNotes || ''
  formData.topicId = excerpt.topic ? excerpt.topic.id : null

  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (excerpt: ProgramExcerpt) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除《${excerpt.programName}》这条记录吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    deletingId.value = excerpt.id
    await excerptApi.delete(excerpt.id)
    ElMessage.success('删除成功！')
    loadExcerpts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
    }
  } finally {
    deletingId.value = null
  }
}

const openConfirmDialog = (excerpt: ProgramExcerpt, action: 'confirmed' | 'needs_verification') => {
  confirmingExcerpt.value = excerpt
  confirmAction.value = action
  confirmNote.value = ''
  generateFollowup.value = true
  confirmDialogVisible.value = true
}

const handleConfirm = async () => {
  if (!confirmingExcerpt.value) return

  if (confirmAction.value === 'needs_verification' && !confirmNote.value.trim()) {
    ElMessage.warning('标记为需核实时必须填写备注')
    return
  }

  confirming.value = true
  try {
    await excerptApi.confirm(
      confirmingExcerpt.value.id,
      confirmAction.value,
      confirmNote.value.trim(),
      generateFollowup.value
    )
    ElMessage.success(confirmAction.value === 'confirmed' ? '已确认！' : '已标记为需核实！')
    confirmDialogVisible.value = false
    loadExcerpts()
  } catch (error: any) {
    const msg = error?.response?.data?.error || '确认操作失败'
    ElMessage.error(msg)
  } finally {
    confirming.value = false
  }
}

const resetForm = () => {
  editingId.value = null
  formData.date = today
  formData.programName = ''
  formData.timeSlot = ''
  formData.contentSummary = ''
  formData.elderlyNotes = ''
  formData.topicId = null
  formRef.value?.resetFields()
}

onMounted(() => {
  loadTopics()
  loadExcerpts()
})
</script>
