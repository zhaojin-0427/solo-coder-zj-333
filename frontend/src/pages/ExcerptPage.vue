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

              <el-divider class="my-4" />

              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  创建于 {{ formatTime(excerpt.createdAt) }}
                </div>
                <div class="flex gap-2">
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
const includeDuplicates = ref(false)

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

const formatTime = (timeStr: string) => {
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
      includeDuplicates: includeDuplicates.value
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
