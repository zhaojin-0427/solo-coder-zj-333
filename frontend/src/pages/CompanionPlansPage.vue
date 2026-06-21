<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📋</span>
      <span>陪办计划</span>
      <el-button
        v-if="userStore.user?.role !== 'elderly'"
        type="primary"
        size="large"
        class="ml-auto"
        @click="openCreateDialog"
      >
        ➕ 新建陪办计划
      </el-button>
    </h1>

    <div class="mb-6">
      <el-radio-group v-model="filterStatus" size="large" @change="loadPlans">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="pending">待办理</el-radio-button>
        <el-radio-button value="preparing">准备中</el-radio-button>
        <el-radio-button value="scheduled">已预约</el-radio-button>
        <el-radio-button value="completed">已完成</el-radio-button>
        <el-radio-button value="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="loading" class="loading-container py-16">
      <div class="text-gray-500 text-lg">⏳ 加载中...</div>
    </div>

    <div v-else-if="plans.length === 0" class="loading-container py-16">
      <el-empty description="暂无陪办计划，点击右上角创建第一个计划吧！" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <el-card
        v-for="plan in plans"
        :key="plan.id"
        class="shadow-card-hover cursor-pointer plan-card"
        :body-style="{ padding: '20px' }"
        @click="goToDetail(plan.id)"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-semibold line-clamp-1">{{ plan.title }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              创建人：{{ plan.createdByName }} · {{ formatDate(plan.createdAt) }}
            </p>
          </div>
          <el-tag :type="getStatusType(plan.status)" size="large" effect="dark">
            {{ plan.statusDisplay }}
          </el-tag>
        </div>

        <div class="space-y-2 mb-3">
          <div class="flex items-center gap-2 text-base text-gray-600">
            <span>📍</span>
            <span class="line-clamp-1">{{ plan.handleLocation }}</span>
          </div>
          <div class="flex items-center gap-2 text-base text-gray-600">
            <span>🕐</span>
            <span>{{ formatTimeRange(plan.handleTimeStart, plan.handleTimeEnd, plan.handleTimeNote) }}</span>
          </div>
          <div v-if="plan.transportationDisplay" class="flex items-center gap-2 text-base text-gray-600">
            <span>🚗</span>
            <span>{{ plan.transportationDisplay }}{{ plan.transportationNote ? ' · ' + plan.transportationNote : '' }}</span>
          </div>
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <el-tag size="large" type="info">
            📄 材料 {{ plan.preparedMaterialCount }}/{{ plan.materialCount }}
            <span v-if="plan.materialCount > 0">
              ({{ Math.round(plan.materialPreparedRate * 100) }}%)
            </span>
          </el-tag>
          <el-tag v-if="plan.companionUserName" size="large" type="warning">
            👨‍👩‍👧 {{ plan.companionUserName }}
          </el-tag>
          <el-tag v-if="plan.sourceTypeDisplay" size="large" effect="plain">
            {{ plan.sourceTypeDisplay }}
          </el-tag>
        </div>

        <el-divider class="my-2" />

        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-500">点击查看详情 →</span>
          <div class="flex items-center gap-1" @click.stop>
            <el-button
              v-if="userStore.user?.role !== 'elderly'"
              type="primary"
              link
              size="small"
              @click="openEditDialog(plan)"
            >
              ✏️ 编辑
            </el-button>
            <el-button
              v-if="userStore.user?.role !== 'elderly'"
              type="danger"
              link
              size="small"
              @click="handleDelete(plan)"
            >
              🗑️ 删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '✏️ 编辑陪办计划' : '📋 新建陪办计划'"
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
        <el-form-item label="事项标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入事项标题，例如：办理社保卡"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="信息来源" prop="sourceType">
              <el-select v-model="formData.sourceType" placeholder="请选择信息来源" style="width: 100%">
                <el-option label="节目摘录" value="excerpt" />
                <el-option label="专题" value="topic" />
                <el-option label="手动输入" value="manual" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item v-if="formData.sourceType === 'excerpt'" label="选择节目摘录" prop="sourceExcerptId">
              <el-select v-model="formData.sourceExcerptId" placeholder="请选择节目摘录" style="width: 100%" filterable>
                <el-option
                  v-for="excerpt in availableExcerpts"
                  :key="excerpt.id"
                  :label="`${excerpt.programName} - ${excerpt.date}`"
                  :value="excerpt.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item v-else-if="formData.sourceType === 'topic'" label="选择专题" prop="sourceTopicId">
              <el-select v-model="formData.sourceTopicId" placeholder="请选择专题" style="width: 100%">
                <el-option
                  v-for="topic in availableTopics"
                  :key="topic.id"
                  :label="topic.name"
                  :value="topic.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item v-else label="来源说明">
              <el-input v-model="formData.sourceExcerptContent" placeholder="请输入来源说明（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item v-if="formData.sourceType === 'excerpt' && selectedExcerpt" label="来源内容预览">
          <div class="bg-orange-50 p-4 rounded-lg border border-orange-100">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-semibold">📻 {{ selectedExcerpt.programName }}</span>
              <span class="text-sm text-gray-500">📅 {{ selectedExcerpt.date }}</span>
              <el-tag
                v-if="selectedExcerpt.topic"
                :style="{ backgroundColor: selectedExcerpt.topic.color + '20', color: selectedExcerpt.topic.color }"
                size="small"
              >
                {{ selectedExcerpt.topic.icon }} {{ selectedExcerpt.topic.name }}
              </el-tag>
            </div>
            <p class="text-sm text-gray-600">{{ selectedExcerpt.contentSummary }}</p>
          </div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="办理地点" prop="handleLocation">
              <el-input v-model="formData.handleLocation" placeholder="请输入办理地点，例如：XX区政务服务中心" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时间窗口说明">
              <el-input v-model="formData.handleTimeNote" placeholder="例如：上午9点-11点，建议早点去排队" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="办理开始时间">
              <el-date-picker
                v-model="formData.handleTimeStart"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="办理结束时间">
              <el-date-picker
                v-model="formData.handleTimeEnd"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="出行方式">
              <el-select v-model="formData.transportation" placeholder="请选择出行方式" style="width: 100%" clearable>
                <el-option label="步行" value="walk" />
                <el-option label="公交" value="bus" />
                <el-option label="地铁" value="subway" />
                <el-option label="出租车" value="taxi" />
                <el-option label="私家车" value="private_car" />
                <el-option label="社区班车" value="community_shuttle" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出行说明">
              <el-input v-model="formData.transportationNote" placeholder="例如：乘坐3号线到XX站A出口" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="陪同家属">
              <el-select v-model="formData.companionUserId" placeholder="请选择陪同家属" style="width: 100%" clearable filterable>
                <el-option
                  v-for="member in familyMembers"
                  :key="member.id"
                  :label="`${member.firstName}${member.lastName} (${member.roleDisplay})`"
                  :value="member.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item v-if="isEditing" label="计划状态">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="待办理" value="pending" />
                <el-option label="准备中" value="preparing" />
                <el-option label="已预约" value="scheduled" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="老人注意事项">
          <el-input
            v-model="formData.elderlyNotes"
            type="textarea"
            :rows="2"
            placeholder="例如：记得带上老花镜，保持空腹不要喝水"
          />
        </el-form-item>

        <el-form-item label="所需材料清单">
          <div class="materials-list space-y-3">
            <div
              v-for="(material, index) in formData.materials"
              :key="index"
              class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
            >
              <span class="w-8 h-8 flex items-center justify-center rounded-full bg-primary text-white font-bold text-sm shrink-0">
                {{ index + 1 }}
              </span>
              <div class="flex-1 space-y-2">
                <el-input
                  v-model="material.name"
                  placeholder="材料名称，例如：身份证原件"
                  size="default"
                />
                <el-input
                  v-model="material.description"
                  placeholder="材料说明（可选），例如：需要正反面复印件"
                  size="default"
                />
              </div>
              <el-button
                type="danger"
                link
                @click="removeMaterial(index)"
                :disabled="formData.materials.length <= 1"
              >
                ✕
              </el-button>
            </div>
            <el-button type="primary" link @click="addMaterial">
              ➕ 添加材料
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="dialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ isEditing ? '保存修改' : '创建计划' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { CompanionPlan, CompanionPlanMaterial, FamilyMember, ProgramExcerpt, Topic } from '@/types'
import { companionPlanApi, familyApi, excerptApi, topicApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const plans = ref<CompanionPlan[]>([])
const filterStatus = ref('')
const familyMembers = ref<FamilyMember[]>([])
const availableExcerpts = ref<ProgramExcerpt[]>([])
const availableTopics = ref<Topic[]>([])

const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

interface FormMaterial {
  name: string
  description: string | null
  orderIndex: number
}

const formData = reactive({
  title: '',
  sourceType: 'manual' as 'excerpt' | 'topic' | 'manual',
  sourceExcerptId: null as number | null,
  sourceTopicId: null as number | null,
  sourceExcerptContent: null as string | null,
  handleLocation: '',
  handleTimeStart: null as string | null,
  handleTimeEnd: null as string | null,
  handleTimeNote: null as string | null,
  transportation: null as CompanionPlan['transportation'],
  transportationNote: null as string | null,
  companionUserId: null as number | null,
  elderlyNotes: null as string | null,
  status: 'pending' as CompanionPlan['status'],
  materials: [] as FormMaterial[]
})

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入事项标题', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  sourceType: [
    { required: true, message: '请选择信息来源', trigger: 'change' }
  ],
  handleLocation: [
    { required: true, message: '请输入办理地点', trigger: 'blur' }
  ]
}

const selectedExcerpt = computed(() => {
  if (formData.sourceType === 'excerpt' && formData.sourceExcerptId) {
    return availableExcerpts.value.find(e => e.id === formData.sourceExcerptId) || null
  }
  return null
})

const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'danger' | 'primary' => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'cancelled':
      return 'danger'
    case 'scheduled':
      return 'primary'
    case 'preparing':
      return 'warning'
    default:
      return 'info'
  }
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

const formatTimeRange = (start: string | null, end: string | null, note: string | null) => {
  if (note) return note
  if (start && end) {
    const startDate = new Date(start)
    const endDate = new Date(end)
    const startStr = startDate.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
    const endStr = endDate.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
    return `${startStr} - ${endStr}`
  }
  if (start) {
    return new Date(start).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  return '待定'
}

const addMaterial = () => {
  formData.materials.push({
    name: '',
    description: null,
    orderIndex: formData.materials.length
  })
}

const removeMaterial = (index: number) => {
  formData.materials.splice(index, 1)
  formData.materials.forEach((m, i) => {
    m.orderIndex = i
  })
}

const resetForm = () => {
  formData.title = ''
  formData.sourceType = 'manual'
  formData.sourceExcerptId = null
  formData.sourceTopicId = null
  formData.sourceExcerptContent = null
  formData.handleLocation = ''
  formData.handleTimeStart = null
  formData.handleTimeEnd = null
  formData.handleTimeNote = null
  formData.transportation = null
  formData.transportationNote = null
  formData.companionUserId = null
  formData.elderlyNotes = null
  formData.status = 'pending'
  formData.materials = []
  addMaterial()
}

const loadPlans = async () => {
  loading.value = true
  try {
    plans.value = await companionPlanApi.getList(filterStatus.value || undefined)
  } catch (error) {
    console.error('Failed to load plans:', error)
  } finally {
    loading.value = false
  }
}

const loadFamilyMembers = async () => {
  try {
    familyMembers.value = await familyApi.getMembers()
  } catch (error) {
    console.error('Failed to load family members:', error)
  }
}

const loadExcerpts = async () => {
  try {
    availableExcerpts.value = await excerptApi.getList()
  } catch (error) {
    console.error('Failed to load excerpts:', error)
  }
}

const loadTopics = async () => {
  try {
    availableTopics.value = await topicApi.getList()
  } catch (error) {
    console.error('Failed to load topics:', error)
  }
}

const openCreateDialog = async () => {
  isEditing.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
  await Promise.all([loadFamilyMembers(), loadExcerpts(), loadTopics()])
}

const openEditDialog = async (plan: CompanionPlan) => {
  isEditing.value = true
  editingId.value = plan.id
  resetForm()

  formData.title = plan.title
  formData.sourceType = plan.sourceType
  formData.sourceExcerptId = plan.sourceExcerptId ?? null
  formData.sourceTopicId = plan.sourceTopicId ?? null
  formData.sourceExcerptContent = plan.sourceExcerptContent
  formData.handleLocation = plan.handleLocation
  formData.handleTimeStart = plan.handleTimeStart
  formData.handleTimeEnd = plan.handleTimeEnd
  formData.handleTimeNote = plan.handleTimeNote
  formData.transportation = plan.transportation
  formData.transportationNote = plan.transportationNote
  formData.companionUserId = plan.companionUserId ?? null
  formData.elderlyNotes = plan.elderlyNotes
  formData.status = plan.status

  if (plan.materials && plan.materials.length > 0) {
    formData.materials = plan.materials.map((m: CompanionPlanMaterial, i: number) => ({
      name: m.name,
      description: m.description,
      orderIndex: i
    }))
  }

  dialogVisible.value = true
  await Promise.all([loadFamilyMembers(), loadExcerpts(), loadTopics()])
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const materials = formData.materials
          .filter(m => m.name.trim())
          .map((m, i) => ({
            name: m.name.trim(),
            description: m.description?.trim() || null,
            orderIndex: i
          }))

        if (isEditing.value && editingId.value) {
          await companionPlanApi.update(editingId.value, {
            title: formData.title,
            sourceType: formData.sourceType,
            sourceExcerptId: formData.sourceType === 'excerpt' ? formData.sourceExcerptId : null,
            sourceTopicId: formData.sourceType === 'topic' ? formData.sourceTopicId : null,
            sourceExcerptContent: formData.sourceType === 'manual' ? formData.sourceExcerptContent : null,
            handleLocation: formData.handleLocation,
            handleTimeStart: formData.handleTimeStart,
            handleTimeEnd: formData.handleTimeEnd,
            handleTimeNote: formData.handleTimeNote,
            transportation: formData.transportation,
            transportationNote: formData.transportationNote,
            companionUserId: formData.companionUserId,
            elderlyNotes: formData.elderlyNotes,
            status: formData.status,
            materials
          })
          ElMessage.success('陪办计划更新成功！')
        } else {
          const result = await companionPlanApi.create({
            title: formData.title,
            sourceType: formData.sourceType,
            sourceExcerptId: formData.sourceType === 'excerpt' ? formData.sourceExcerptId : null,
            sourceTopicId: formData.sourceType === 'topic' ? formData.sourceTopicId : null,
            sourceExcerptContent: formData.sourceType === 'manual' ? formData.sourceExcerptContent : null,
            handleLocation: formData.handleLocation,
            handleTimeStart: formData.handleTimeStart,
            handleTimeEnd: formData.handleTimeEnd,
            handleTimeNote: formData.handleTimeNote,
            transportation: formData.transportation,
            transportationNote: formData.transportationNote,
            companionUserId: formData.companionUserId,
            elderlyNotes: formData.elderlyNotes,
            status: formData.status,
            materials
          })
          ElMessage.success('陪办计划创建成功！')
          dialogVisible.value = false
          loadPlans()
          router.push(`/companion-plans/${result.id}`)
          return
        }

        dialogVisible.value = false
        loadPlans()
      } catch (error) {
        console.error('Submit error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (plan: CompanionPlan) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除陪办计划「${plan.title}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await companionPlanApi.remove(plan.id)
    ElMessage.success('删除成功')
    loadPlans()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
    }
  }
}

const goToDetail = (id: number) => {
  router.push(`/companion-plans/${id}`)
}

watch(() => formData.sourceType, () => {
  formData.sourceExcerptId = null
  formData.sourceTopicId = null
  formData.sourceExcerptContent = null
})

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.plan-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.ml-auto {
  margin-left: auto;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}
</style>
