<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📚</span>
      <span>回听资料包</span>
      <el-button
        v-if="userStore.user?.role !== 'elderly'"
        type="primary"
        size="large"
        class="ml-auto"
        @click="openCreateDialog"
      >
        ➕ 新建资料包
      </el-button>
    </h1>

    <div v-if="loading" class="loading-container py-16">
      <div class="text-gray-500 text-lg">⏳ 加载中...</div>
    </div>

    <div v-else-if="packages.length === 0" class="loading-container py-16">
      <el-empty description="暂无资料包，点击右上角创建第一个资料包吧！" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <el-card
        v-for="pkg in packages"
        :key="pkg.id"
        class="shadow-card-hover cursor-pointer"
        :body-style="{ padding: '20px' }"
        @click="goToDetail(pkg.id)"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-xl font-semibold line-clamp-1">{{ pkg.title }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              创建人：{{ pkg.createdByName }} · {{ formatDate(pkg.createdAt) }}
            </p>
          </div>
        </div>

        <div v-if="pkg.purposeDescription" class="text-base text-gray-600 mb-3 line-clamp-2">
          {{ pkg.purposeDescription }}
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <el-tag size="large" type="info">
            📄 {{ pkg.itemCount }} 条内容
          </el-tag>
          <el-tag size="large" type="success">
            💬 {{ pkg.feedbackCount }} 条反馈
          </el-tag>
        </div>

        <el-divider class="my-2" />

        <div class="flex items-center justify-between text-sm text-gray-500">
          <span>点击查看详情 →</span>
          <span>更新于 {{ formatDate(pkg.updatedAt) }}</span>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="📚 新建回听资料包"
      width="800px"
      size="large"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="资料包标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入资料包标题，例如：健康养生精选"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="用途说明">
              <el-input
                v-model="formData.purposeDescription"
                type="textarea"
                :rows="2"
                placeholder="例如：给爸妈准备的本周健康节目回顾"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="导览语">
              <el-input
                v-model="formData.guideText"
                type="textarea"
                :rows="2"
                placeholder="例如：爸妈，这周的精彩内容都在这里啦，慢慢看～"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="选择节目摘录（1-20条）" prop="excerptIds">
          <div class="excerpt-selector">
            <div class="flex items-center justify-between mb-3">
              <span class="text-base text-gray-600">
                已选择 <span class="font-bold text-primary">{{ formData.excerptIds.length }}</span> / 20 条
              </span>
              <el-button type="primary" link @click="toggleSelectAll">
                {{ isAllSelected ? '取消全选' : '全选当前页' }}
              </el-button>
            </div>

            <div class="excerpt-list max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
              <div
                v-for="excerpt in availableExcerpts"
                :key="excerpt.id"
                class="excerpt-item flex items-start gap-3 p-4 border-b border-gray-100 hover:bg-orange-50 transition-colors"
                :class="{ 'bg-orange-50': isExcerptSelected(excerpt.id) }"
              >
                <el-checkbox
                  :model-value="isExcerptSelected(excerpt.id)"
                  @change="(val: boolean) => toggleExcerpt(excerpt.id, val)"
                />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold">📻 {{ excerpt.programName }}</span>
                    <span class="text-sm text-gray-500">📅 {{ excerpt.date }}</span>
                    <el-tag
                      v-if="excerpt.topic"
                      :style="{ backgroundColor: excerpt.topic.color + '20', color: excerpt.topic.color }"
                      size="small"
                    >
                      {{ excerpt.topic.icon }} {{ excerpt.topic.name }}
                    </el-tag>
                  </div>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ excerpt.contentSummary }}</p>
                </div>
              </div>
              <div v-if="availableExcerpts.length === 0" class="p-8 text-center text-gray-400">
                暂无可选的节目摘录
              </div>
            </div>
          </div>
        </el-form-item>

        <el-form-item v-if="selectedExcerpts.length > 0" label="阅读顺序 / 重点标记 / 家属提醒">
          <div class="selected-items-config border border-gray-200 rounded-lg">
            <div class="bg-orange-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">
                📋 已选条目（可拖拽调整顺序，点击 ⭐ 标记重点）
              </span>
              <span class="text-xs text-gray-500">
                ⬆️⬇️ 调整顺序 &nbsp;|&nbsp; ⭐ 重点标记 &nbsp;|&nbsp; 💬 家属提醒
              </span>
            </div>
            <div class="max-h-96 overflow-y-auto">
              <div
                v-for="(excerpt, index) in selectedExcerpts"
                :key="excerpt.id"
                class="selected-item p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-start gap-3">
                  <div class="flex flex-col items-center gap-1 pt-1">
                    <span class="w-6 h-6 flex items-center justify-center rounded-full bg-primary text-white text-sm font-bold">
                      {{ index + 1 }}
                    </span>
                    <div class="flex flex-col">
                      <el-button
                        size="small"
                        text
                        :disabled="index === 0"
                        @click="moveItemUp(index)"
                        class="h-6 !px-1"
                      >
                        ⬆️
                      </el-button>
                      <el-button
                        size="small"
                        text
                        :disabled="index === selectedExcerpts.length - 1"
                        @click="moveItemDown(index)"
                        class="h-6 !px-1"
                      >
                        ⬇️
                      </el-button>
                    </div>
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1 flex-wrap">
                      <span class="font-semibold truncate">📻 {{ excerpt.programName }}</span>
                      <span class="text-sm text-gray-500">{{ excerpt.date }}</span>
                      <el-tag
                        v-if="excerpt.topic"
                        :style="{ backgroundColor: excerpt.topic.color + '20', color: excerpt.topic.color }"
                        size="small"
                      >
                        {{ excerpt.topic.icon }} {{ excerpt.topic.name }}
                      </el-tag>
                    </div>
                    <p class="text-sm text-gray-600 line-clamp-1 mb-2">{{ excerpt.contentSummary }}</p>

                    <div class="flex items-center gap-4 flex-wrap">
                      <el-checkbox
                        :model-value="getItemConfig(excerpt.id).isHighlighted"
                        @change="(val: boolean) => setItemHighlight(excerpt.id, val)"
                      >
                        ⭐ 标记为重点
                      </el-checkbox>

                      <div class="flex items-center gap-2 flex-1 min-w-[200px]">
                        <span class="text-sm text-gray-500 shrink-0">💬 家属提醒：</span>
                        <el-input
                          :model-value="getItemConfig(excerpt.id).familyReminder"
                          @update:model-value="(val: string) => setItemReminder(excerpt.id, val)"
                          size="small"
                          placeholder="给老人看的提醒，例如：这条很重要，要仔细看"
                          class="flex-1"
                        />
                      </div>
                    </div>
                  </div>

                  <el-button
                    size="small"
                    text
                    type="danger"
                    @click="toggleExcerpt(excerpt.id, false)"
                  >
                    ✕ 移除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="createDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          :disabled="formData.excerptIds.length === 0"
          @click="handleCreate"
        >
          创建资料包
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { ReviewPackage, ProgramExcerpt } from '@/types'
import { reviewPackageApi, excerptApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const packages = ref<ReviewPackage[]>([])
const availableExcerpts = ref<ProgramExcerpt[]>([])

const createDialogVisible = ref(false)
const formRef = ref<FormInstance>()

const formData = reactive({
  title: '',
  purposeDescription: '',
  guideText: '',
  excerptIds: [] as number[]
})

const itemsConfig = reactive<Record<number, { isHighlighted: boolean; familyReminder: string }>>({})

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入资料包标题', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  excerptIds: [
    { required: true, message: '请至少选择一条节目摘录', trigger: 'change' },
    {
      validator: (_rule, value, callback) => {
        if (value.length === 0) {
          callback(new Error('请至少选择一条节目摘录'))
        } else if (value.length > 20) {
          callback(new Error('最多只能选择 20 条节目摘录'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const isAllSelected = computed(() => {
  return availableExcerpts.value.length > 0 &&
    availableExcerpts.value.every(e => formData.excerptIds.includes(e.id))
})

const selectedExcerpts = computed(() => {
  return formData.excerptIds
    .map(id => availableExcerpts.value.find(e => e.id === id))
    .filter((e): e is ProgramExcerpt => !!e)
})

const getItemConfig = (excerptId: number) => {
  if (!itemsConfig[excerptId]) {
    itemsConfig[excerptId] = { isHighlighted: false, familyReminder: '' }
  }
  return itemsConfig[excerptId]
}

const setItemHighlight = (excerptId: number, highlighted: boolean) => {
  getItemConfig(excerptId).isHighlighted = highlighted
}

const setItemReminder = (excerptId: number, reminder: string) => {
  getItemConfig(excerptId).familyReminder = reminder
}

const moveItemUp = (index: number) => {
  if (index <= 0) return
  const ids = [...formData.excerptIds]
  ;[ids[index - 1], ids[index]] = [ids[index], ids[index - 1]]
  formData.excerptIds = ids
}

const moveItemDown = (index: number) => {
  if (index >= formData.excerptIds.length - 1) return
  const ids = [...formData.excerptIds]
  ;[ids[index], ids[index + 1]] = [ids[index + 1], ids[index]]
  formData.excerptIds = ids
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const isExcerptSelected = (excerptId: number) => {
  return formData.excerptIds.includes(excerptId)
}

const toggleExcerpt = (excerptId: number, selected: boolean) => {
  if (selected) {
    if (formData.excerptIds.length >= 20) {
      ElMessage.warning('最多只能选择 20 条节目摘录')
      return
    }
    formData.excerptIds.push(excerptId)
    if (!itemsConfig[excerptId]) {
      itemsConfig[excerptId] = { isHighlighted: false, familyReminder: '' }
    }
  } else {
    formData.excerptIds = formData.excerptIds.filter(id => id !== excerptId)
    delete itemsConfig[excerptId]
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    formData.excerptIds = []
    Object.keys(itemsConfig).forEach(key => delete itemsConfig[Number(key)])
  } else {
    const ids = availableExcerpts.value.map(e => e.id)
    const combined = [...new Set([...formData.excerptIds, ...ids])]
    formData.excerptIds = combined.slice(0, 20)
    formData.excerptIds.forEach(id => {
      if (!itemsConfig[id]) {
        itemsConfig[id] = { isHighlighted: false, familyReminder: '' }
      }
    })
  }
}

const loadPackages = async () => {
  loading.value = true
  try {
    packages.value = await reviewPackageApi.getList()
  } catch (error) {
    console.error('Failed to load packages:', error)
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

const openCreateDialog = () => {
  formData.title = ''
  formData.purposeDescription = ''
  formData.guideText = ''
  formData.excerptIds = []
  Object.keys(itemsConfig).forEach(key => delete itemsConfig[Number(key)])
  createDialogVisible.value = true
  loadExcerpts()
}

const handleCreate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const finalItemsConfig: Record<string, { isHighlighted?: boolean; familyReminder?: string }> = {}
        Object.entries(itemsConfig).forEach(([idStr, config]) => {
          if (config.isHighlighted || config.familyReminder) {
            finalItemsConfig[idStr] = {
              isHighlighted: config.isHighlighted,
              familyReminder: config.familyReminder
            }
          }
        })

        const result = await reviewPackageApi.create({
          title: formData.title,
          purposeDescription: formData.purposeDescription || null,
          guideText: formData.guideText || null,
          excerptIds: formData.excerptIds,
          itemsConfig: Object.keys(finalItemsConfig).length > 0 ? finalItemsConfig : undefined
        })
        ElMessage.success('资料包创建成功！')
        createDialogVisible.value = false
        loadPackages()
        router.push(`/review-packages/${result.id}`)
      } catch (error) {
        console.error('Create package error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const goToDetail = (id: number) => {
  router.push(`/review-packages/${id}`)
}

onMounted(() => {
  loadPackages()
})
</script>

<style scoped>
.excerpt-selector .excerpt-item:last-child {
  border-bottom: none;
}
</style>
