<template>
  <div class="page-container">
    <div class="flex items-center gap-4 mb-8">
      <el-button size="large" @click="router.back()" class="elderly-back-btn">
        <span class="text-xl">←</span>
        <span class="text-xl ml-2">返回</span>
      </el-button>
      <h1 class="page-title mb-0">
        <span>📋</span>
        <span class="text-3xl font-bold">陪办计划详情</span>
      </h1>
    </div>

    <div v-if="loading" class="loading-container py-16">
      <div class="text-gray-500 text-2xl">⏳ 加载中，请稍候...</div>
    </div>

    <div v-else-if="!planData" class="loading-container py-16">
      <el-empty description="陪办计划不存在" />
    </div>

    <template v-else>
      <div v-if="isElderly" class="elderly-view">
        <div class="elderly-section mb-8">
          <h2 class="section-title text-2xl font-bold mb-6">
            <span>📌</span>
            <span>办理信息</span>
          </h2>

          <el-card class="shadow-card elderly-info-card" :body-style="{ padding: '32px' }">
            <div class="space-y-6">
              <div class="elderly-info-item">
                <span class="elderly-info-label text-xl">事项名称：</span>
                <span class="elderly-info-value text-2xl font-bold text-primary">{{ planData.title }}</span>
              </div>

              <div class="elderly-info-item">
                <span class="elderly-info-label text-xl">办理地点：</span>
                <span class="elderly-info-value text-xl font-semibold">📍 {{ planData.handleLocation }}</span>
              </div>

              <div class="elderly-time-box">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-2xl">⏰</span>
                  <span class="text-xl font-bold">办理时间</span>
                </div>
                <div class="text-3xl font-bold text-primary pl-10">
                  {{ formatHandleTime(planData.handleTimeStart, planData.handleTimeEnd) }}
                </div>
                <div v-if="planData.handleTimeNote" class="text-xl text-gray-600 pl-10 mt-2">
                  📝 {{ planData.handleTimeNote }}
                </div>
              </div>

              <div class="elderly-info-item">
                <span class="elderly-info-label text-xl">出行方式：</span>
                <span class="elderly-info-value text-xl font-semibold">
                  {{ getTransportationIcon(planData.transportation) }} {{ planData.transportationDisplay || '暂无' }}
                </span>
              </div>

              <div class="elderly-info-item">
                <span class="elderly-info-label text-xl">陪同家属：</span>
                <span class="elderly-info-value text-xl font-semibold">
                  👨‍👩‍👧 {{ planData.companionUserName || '暂无' }}
                </span>
              </div>
            </div>
          </el-card>
        </div>

        <div class="elderly-section mb-8">
          <h2 class="section-title text-2xl font-bold mb-6">
            <span>📂</span>
            <span>材料清单</span>
            <span class="text-lg font-normal text-gray-500 ml-3">
              (已准备 {{ preparedMaterialCount }}/{{ allMaterials.length }})
            </span>
          </h2>

          <div v-if="allMaterials.length === 0" class="py-8">
            <el-empty description="暂无需要准备的材料" />
          </div>

          <div v-else class="space-y-4">
            <el-card
              v-for="material in sortedMaterials"
              :key="material.id"
              class="material-card shadow-card-hover"
              :class="{ 'material-prepared': material.isPrepared }"
              :body-style="{ padding: '24px' }"
              @click="toggleMaterial(material)"
            >
              <div class="flex items-start gap-6">
                <el-checkbox
                  :model-value="material.isPrepared"
                  size="large"
                  class="elderly-checkbox"
                  @change="toggleMaterial(material)"
                />
                <div class="flex-1">
                  <div class="text-2xl font-bold mb-2" :class="{ 'line-through text-gray-400': material.isPrepared }">
                    📄 {{ material.name }}
                  </div>
                  <div v-if="material.description" class="text-xl text-gray-600">
                    {{ material.description }}
                  </div>
                  <div v-if="material.isPrepared && material.preparedByName" class="text-lg text-green-600 mt-2">
                    ✅ 已由 {{ material.preparedByName }} 于 {{ formatDateTime(material.preparedAt) }} 确认准备好
                  </div>
                </div>
                <div class="text-4xl">
                  {{ material.isPrepared ? '✅' : '⬜' }}
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <div class="elderly-section mb-8">
          <h2 class="section-title text-2xl font-bold mb-6">
            <span>✔️</span>
            <span>请确认以下事项</span>
          </h2>

          <div class="space-y-6">
            <el-card class="confirmation-card shadow-card-hover" :body-style="{ padding: '24px' }">
              <div class="flex items-center gap-6" @click="formData.materialsConfirmed = !formData.materialsConfirmed">
                <el-checkbox
                  v-model="formData.materialsConfirmed"
                  size="large"
                  class="elderly-checkbox"
                />
                <span class="text-2xl font-semibold">✅ 材料已准备好</span>
              </div>
            </el-card>

            <el-card class="confirmation-card shadow-card-hover" :body-style="{ padding: '24px' }">
              <div class="flex items-center gap-6" @click="formData.timeLocationKnown = !formData.timeLocationKnown">
                <el-checkbox
                  v-model="formData.timeLocationKnown"
                  size="large"
                  class="elderly-checkbox"
                />
                <span class="text-2xl font-semibold">✅ 我已知晓办理时间和地点</span>
              </div>
            </el-card>

            <el-card class="confirmation-card shadow-card-hover" :class="{ 'needs-companion': formData.needsCompanion }" :body-style="{ padding: '24px' }">
              <div class="flex items-center gap-6" @click="toggleNeedsCompanion">
                <el-checkbox
                  v-model="formData.needsCompanion"
                  size="large"
                  class="elderly-checkbox"
                />
                <span class="text-2xl font-semibold">✅ 需要家人陪同前往</span>
              </div>
              <div v-if="formData.needsCompanion" class="mt-4 pl-16 p-4 bg-green-50 rounded-xl">
                <div class="text-xl text-green-700 font-semibold">
                  💡 已为您通知家人，他们会尽快安排时间陪同您前往
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <div class="elderly-section mb-8">
          <h2 class="section-title text-2xl font-bold mb-6">
            <span>💭</span>
            <span>您有什么担心的问题吗？</span>
          </h2>

          <el-input
            v-model="formData.elderlyConcerns"
            type="textarea"
            :rows="5"
            placeholder="如果您对这次办理有任何担心、疑问或想让家人帮忙确认的事情，请写在这里..."
            size="large"
            class="elderly-textarea"
          />
          <p class="text-lg text-gray-500 mt-3">
            💡 写下来后，家人会看到并帮您处理
          </p>
        </div>

        <div class="flex justify-center">
          <el-button
            type="primary"
            size="large"
            class="elderly-save-btn"
            :loading="submitting"
            @click="handleElderlyCheckin"
          >
            <span class="text-2xl px-8 py-4 inline-block">💾 保存确认</span>
          </el-button>
        </div>
      </div>

      <div v-else class="family-view">
        <el-card class="shadow-card mb-8" :body-style="{ padding: '32px' }">
          <div class="flex items-start justify-between flex-wrap gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-4 mb-4 flex-wrap">
                <h2 class="text-3xl font-bold">{{ planData.title }}</h2>
                <el-tag :type="statusTagType(planData.status)" size="large" effect="dark">
                  {{ planData.statusDisplay }}
                </el-tag>
                <el-tag type="info" size="large">
                  {{ planData.sourceTypeDisplay }}
                </el-tag>
              </div>

              <div class="text-lg text-gray-500 mb-4">
                创建人：{{ planData.createdByName }} · 创建于 {{ formatDateTime(planData.createdAt) }}
              </div>

              <el-descriptions :column="2" border size="large" class="mt-6">
                <el-descriptions-item label="办理地点" label-class-name="desc-label">
                  <span class="text-xl">📍 {{ planData.handleLocation }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="办理时间" label-class-name="desc-label">
                  <span class="text-xl font-semibold text-primary">
                    ⏰ {{ formatHandleTime(planData.handleTimeStart, planData.handleTimeEnd) }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="时间说明" label-class-name="desc-label">
                  <span v-if="planData.handleTimeNote">{{ planData.handleTimeNote }}</span>
                  <span v-else class="text-gray-400">暂无</span>
                </el-descriptions-item>
                <el-descriptions-item label="出行方式" label-class-name="desc-label">
                  <span v-if="planData.transportationDisplay">
                    {{ getTransportationIcon(planData.transportation) }} {{ planData.transportationDisplay }}
                  </span>
                  <span v-else class="text-gray-400">未安排</span>
                  <span v-if="planData.transportationNote" class="ml-2 text-gray-500">
                    ({{ planData.transportationNote }})
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="陪同家属" label-class-name="desc-label">
                  <span v-if="planData.companionUserName">👨‍👩‍👧 {{ planData.companionUserName }}</span>
                  <span v-else class="text-gray-400">未安排</span>
                </el-descriptions-item>
                <el-descriptions-item label="材料准备进度" label-class-name="desc-label">
                  <div class="flex items-center gap-3">
                    <el-progress
                      :percentage="Math.round(planData.materialPreparedRate * 100)"
                      :color="planData.materialPreparedRate === 1 ? '#52C41A' : '#FF7A45'"
                      :stroke-width="14"
                    />
                    <span class="text-lg font-semibold">
                      {{ planData.preparedMaterialCount }}/{{ planData.materialCount }}
                    </span>
                  </div>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="flex flex-col gap-3">
              <el-button type="primary" size="large" @click="openEditDialog">
                ✏️ 编辑计划
              </el-button>
              <el-button
                size="large"
                :type="planData.status !== 'completed' ? 'success' : 'info'"
                @click="togglePlanStatus"
              >
                {{ planData.status === 'completed' ? '↩️ 重新打开' : '✅ 标记已完成' }}
              </el-button>
              <el-button type="danger" size="large" @click="confirmDelete">
                🗑️ 删除计划
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card class="shadow-card mb-8" :body-style="{ padding: '32px' }">
          <h3 class="text-2xl font-bold mb-6">
            <span>✔️</span>
            <span>老人确认状态</span>
          </h3>

          <el-row :gutter="24">
            <el-col :xs="24" :md="8">
              <div class="status-item" :class="{ 'status-confirmed': planData.materialsConfirmed }">
                <div class="text-4xl mb-3">{{ planData.materialsConfirmed ? '✅' : '⬜' }}</div>
                <div class="text-xl font-semibold">材料已准备</div>
                <div class="text-sm text-gray-500 mt-1">
                  {{ planData.materialsConfirmed ? '已确认' : '待确认' }}
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :md="8">
              <div class="status-item" :class="{ 'status-confirmed': planData.timeLocationKnown }">
                <div class="text-4xl mb-3">{{ planData.timeLocationKnown ? '✅' : '⬜' }}</div>
                <div class="text-xl font-semibold">知晓时间地点</div>
                <div class="text-sm text-gray-500 mt-1">
                  {{ planData.timeLocationKnown ? '已确认' : '待确认' }}
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :md="8">
              <div class="status-item" :class="{ 'status-confirmed': planData.needsCompanion }">
                <div class="text-4xl mb-3">{{ planData.needsCompanion ? '✅' : '⬜' }}</div>
                <div class="text-xl font-semibold">需要家人陪同</div>
                <div class="text-sm text-gray-500 mt-1">
                  {{ planData.needsCompanion ? '需要陪同' : '暂不需要' }}
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <div v-if="planData.elderlyConcerns" class="concerns-box">
            <div class="flex items-center gap-3 mb-3">
              <span class="text-2xl">💭</span>
              <span class="text-xl font-bold">老人担心的问题</span>
            </div>
            <div class="text-xl text-gray-700 bg-orange-50 p-6 rounded-xl border-l-4 border-orange-400">
              {{ planData.elderlyConcerns }}
            </div>
          </div>
          <div v-else class="text-lg text-gray-400 text-center py-4">
            老人暂无记录担心的问题
          </div>

          <div v-if="planData.elderlyNotes" class="mt-6">
            <div class="flex items-center gap-3 mb-3">
              <span class="text-2xl">📝</span>
              <span class="text-xl font-bold">老人备注</span>
            </div>
            <div class="text-lg text-gray-700 bg-gray-50 p-4 rounded-xl">
              {{ planData.elderlyNotes }}
            </div>
          </div>
        </el-card>

        <el-card class="shadow-card mb-8" :body-style="{ padding: '32px' }">
          <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
            <h3 class="text-2xl font-bold">
              <span>📂</span>
              <span>材料管理</span>
              <span class="text-lg font-normal text-gray-500 ml-3">
                ({{ planData.preparedMaterialCount }}/{{ planData.materialCount }} 已准备)
              </span>
            </h3>
            <el-button type="primary" size="large" @click="openAddMaterialDialog">
              ➕ 添加材料
            </el-button>
          </div>

          <div v-if="allMaterials.length === 0" class="py-8">
            <el-empty description="暂无材料，点击上方按钮添加" />
          </div>

          <div v-else class="space-y-4">
            <el-card
              v-for="(material, index) in sortedMaterials"
              :key="material.id"
              class="material-card shadow-card-hover"
              :class="{ 'material-prepared': material.isPrepared }"
              :body-style="{ padding: '24px' }"
            >
              <div class="flex items-start justify-between gap-6">
                <div class="flex items-start gap-6 flex-1">
                  <div class="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center text-xl font-bold">
                    {{ index + 1 }}
                  </div>
                  <div class="flex-1">
                    <div class="text-2xl font-bold mb-2" :class="{ 'line-through text-gray-400': material.isPrepared }">
                      📄 {{ material.name }}
                    </div>
                    <div v-if="material.description" class="text-lg text-gray-600 mb-3">
                      {{ material.description }}
                    </div>
                    <div v-if="material.isPrepared" class="text-lg text-green-600">
                      ✅ 已由 {{ material.preparedByName || '未知' }} 于 {{ formatDateTime(material.preparedAt) }} 确认准备好
                    </div>
                  </div>
                </div>
                <div class="flex flex-col gap-2">
                  <el-button
                    size="large"
                    :type="material.isPrepared ? 'info' : 'success'"
                    @click="toggleMaterialStatus(material)"
                  >
                    {{ material.isPrepared ? '↩️ 取消准备' : '✅ 标记已准备' }}
                  </el-button>
                  <el-button size="large" type="danger" @click="confirmDeleteMaterial(material)">
                    🗑️ 删除
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
      </div>
    </template>

    <el-dialog
      v-model="editDialogVisible"
      title="✏️ 编辑陪办计划"
      width="700px"
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
        <el-form-item label="事项标题" prop="title">
          <el-input v-model="editFormData.title" placeholder="输入事项标题" />
        </el-form-item>

        <el-form-item label="办理地点" prop="handleLocation">
          <el-input v-model="editFormData.handleLocation" placeholder="输入办理地点" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="办理开始时间">
              <el-date-picker
                v-model="editFormData.handleTimeStart"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="办理结束时间">
              <el-date-picker
                v-model="editFormData.handleTimeEnd"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="时间说明">
          <el-input
            v-model="editFormData.handleTimeNote"
            type="textarea"
            :rows="2"
            placeholder="例如：上午人少，建议早去..."
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="出行方式">
              <el-select v-model="editFormData.transportation" placeholder="选择出行方式" style="width: 100%" clearable>
                <el-option label="🚶 步行" value="walk" />
                <el-option label="🚌 公交车" value="bus" />
                <el-option label="🚇 地铁" value="subway" />
                <el-option label="🚕 出租车" value="taxi" />
                <el-option label="🚗 私家车" value="private_car" />
                <el-option label="🚐 社区班车" value="community_shuttle" />
                <el-option label="🔄 其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="陪同家属">
              <el-select v-model="editFormData.companionUserId" placeholder="选择陪同家属" style="width: 100%" clearable>
                <el-option
                  v-for="member in familyMembers"
                  :key="member.id"
                  :label="member.firstName || member.username"
                  :value="member.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="出行说明">
          <el-input
            v-model="editFormData.transportationNote"
            type="textarea"
            :rows="2"
            placeholder="例如：在XX站下车，走B出口..."
          />
        </el-form-item>

        <el-form-item label="当前状态">
          <el-select v-model="editFormData.status" style="width: 100%">
            <el-option label="⏳ 待处理" value="pending" />
            <el-option label="📋 准备中" value="preparing" />
            <el-option label="📅 已安排" value="scheduled" />
            <el-option label="✅ 已完成" value="completed" />
            <el-option label="❌ 已取消" value="cancelled" />
          </el-select>
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

    <el-dialog
      v-model="addMaterialDialogVisible"
      title="➕ 添加材料"
      width="500px"
      size="large"
    >
      <el-form
        ref="addMaterialFormRef"
        :model="addMaterialFormData"
        :rules="addMaterialFormRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="材料名称" prop="name">
          <el-input v-model="addMaterialFormData.name" placeholder="例如：身份证原件" />
        </el-form-item>
        <el-form-item label="材料说明">
          <el-input
            v-model="addMaterialFormData.description"
            type="textarea"
            :rows="3"
            placeholder="例如：请务必带原件，复印件无效..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button size="large" @click="addMaterialDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submittingMaterial"
          @click="handleAddMaterial"
        >
          添加
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
import type { CompanionPlan, CompanionPlanMaterial, FamilyMember } from '@/types'
import { companionPlanApi, followUpApi, familyApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const submittingEdit = ref(false)
const submittingMaterial = ref(false)

const planData = ref<CompanionPlan | null>(null)
const allMaterials = ref<CompanionPlanMaterial[]>([])
const familyMembers = ref<FamilyMember[]>([])

const formData = reactive({
  materialsConfirmed: false,
  timeLocationKnown: false,
  needsCompanion: false,
  elderlyConcerns: ''
})

const isElderly = computed(() => userStore.user?.role === 'elderly')
const isFamily = computed(() => userStore.user?.role === 'family' || userStore.user?.role === 'admin')

const sortedMaterials = computed(() => {
  return [...allMaterials.value].sort((a, b) => a.orderIndex - b.orderIndex)
})

const preparedMaterialCount = computed(() => {
  return allMaterials.value.filter(m => m.isPrepared).length
})

const formatDateTime = (dateStr?: string | null) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatHandleTime = (start?: string | null, end?: string | null) => {
  if (!start && !end) return '暂无安排'
  const formatPart = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  if (start && end) return `${formatPart(start)} ~ ${formatPart(end)}`
  if (start) return formatPart(start)
  if (end) return formatPart(end)
  return '暂无安排'
}

const getTransportationIcon = (type?: string | null) => {
  const map: Record<string, string> = {
    walk: '🚶',
    bus: '🚌',
    subway: '🚇',
    taxi: '🚕',
    private_car: '🚗',
    community_shuttle: '🚐',
    other: '🔄'
  }
  return map[type || ''] || '📍'
}

const statusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    preparing: '',
    scheduled: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const loadPlan = async () => {
  const id = Number(route.params.id)
  if (!id) return

  loading.value = true
  try {
    planData.value = await companionPlanApi.getDetail(id)
    if (planData.value.materials) {
      allMaterials.value = planData.value.materials
    } else {
      allMaterials.value = await companionPlanApi.getMaterials(id)
    }

    if (isElderly.value) {
      formData.materialsConfirmed = planData.value.materialsConfirmed
      formData.timeLocationKnown = planData.value.timeLocationKnown
      formData.needsCompanion = planData.value.needsCompanion
      formData.elderlyConcerns = planData.value.elderlyConcerns || ''
    }
  } catch (error) {
    console.error('Failed to load plan:', error)
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

const toggleMaterial = async (material: CompanionPlanMaterial) => {
  if (!isElderly.value) return

  try {
    const updated = await companionPlanApi.updateMaterialStatus(material.id, !material.isPrepared)
    const idx = allMaterials.value.findIndex(m => m.id === material.id)
    if (idx !== -1) {
      allMaterials.value[idx] = updated
    }
    ElMessage.success(updated.isPrepared ? '已标记为已准备' : '已取消准备状态')
  } catch (error) {
    console.error('Toggle material error:', error)
  }
}

const toggleNeedsCompanion = () => {
  formData.needsCompanion = !formData.needsCompanion
}

const handleElderlyCheckin = async () => {
  const id = Number(route.params.id)
  if (!id) return

  submitting.value = true
  try {
    const preparedMaterialIds = allMaterials.value.filter(m => m.isPrepared).map(m => m.id)

    await companionPlanApi.elderlyCheckin(id, {
      materialsConfirmed: formData.materialsConfirmed,
      timeLocationKnown: formData.timeLocationKnown,
      needsCompanion: formData.needsCompanion,
      elderlyConcerns: formData.elderlyConcerns || null,
      materialIds: preparedMaterialIds
    })

    if (formData.needsCompanion && planData.value && !planData.value.needsCompanion) {
      try {
        const today = new Date()
        const dueDate = new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000)

        await followUpApi.create({
          title: `陪同老人办理「${planData.value.title}」`,
          description: `老人需要家人陪同前往办理事项：${planData.value.title}\n地点：${planData.value.handleLocation}\n时间：${formatHandleTime(planData.value.handleTimeStart, planData.value.handleTimeEnd)}${formData.elderlyConcerns ? `\n老人担心的问题：${formData.elderlyConcerns}` : ''}`,
          status: 'pending',
          priority: 'high',
          sourceType: 'companion_plan',
          companionPlanId: planData.value.id,
          assignedToId: planData.value.companionUserId ?? null,
          dueDate: dueDate.toISOString()
        })
        ElMessage.info('已自动生成陪同待办事项，已通知家人')
      } catch (followupError) {
        console.error('Failed to create followup:', followupError)
      }
    }

    ElMessage.success('✅ 保存成功！您的确认已记录')
    loadPlan()
  } catch (error) {
    console.error('Checkin error:', error)
  } finally {
    submitting.value = false
  }
}

const toggleMaterialStatus = async (material: CompanionPlanMaterial) => {
  try {
    const updated = await companionPlanApi.updateMaterialStatus(material.id, !material.isPrepared)
    const idx = allMaterials.value.findIndex(m => m.id === material.id)
    if (idx !== -1) {
      allMaterials.value[idx] = updated
    }
    if (planData.value) {
      planData.value.preparedMaterialCount = allMaterials.value.filter(m => m.isPrepared).length
      planData.value.materialPreparedRate = planData.value.materialCount > 0
        ? planData.value.preparedMaterialCount / planData.value.materialCount
        : 0
    }
    ElMessage.success(updated.isPrepared ? '已标记为已准备' : '已取消准备状态')
  } catch (error) {
    console.error('Toggle material status error:', error)
  }
}

const confirmDeleteMaterial = async (material: CompanionPlanMaterial) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料「${material.name}」吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('材料已删除')
    loadPlan()
  } catch {
  }
}

const togglePlanStatus = async () => {
  if (!planData.value) return

  const newStatus = planData.value.status === 'completed' ? 'scheduled' : 'completed'
  try {
    await companionPlanApi.update(planData.value.id, { status: newStatus })
    ElMessage.success(newStatus === 'completed' ? '已标记为已完成' : '已重新打开')
    loadPlan()
  } catch (error) {
    console.error('Toggle status error:', error)
  }
}

const confirmDelete = async () => {
  if (!planData.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除陪办计划「${planData.value.title}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await companionPlanApi.remove(planData.value.id)
    ElMessage.success('陪办计划已删除')
    router.push('/companion-plans')
  } catch {
  }
}

const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editFormData = reactive({
  title: '',
  handleLocation: '',
  handleTimeStart: '',
  handleTimeEnd: '',
  handleTimeNote: '',
  transportation: '' as string | null,
  transportationNote: '',
  companionUserId: null as number | null,
  status: 'pending' as CompanionPlan['status']
})

const editFormRules: FormRules = {
  title: [
    { required: true, message: '请输入事项标题', trigger: 'blur' }
  ],
  handleLocation: [
    { required: true, message: '请输入办理地点', trigger: 'blur' }
  ]
}

const openEditDialog = async () => {
  if (!planData.value) return

  editFormData.title = planData.value.title
  editFormData.handleLocation = planData.value.handleLocation
  editFormData.handleTimeStart = planData.value.handleTimeStart || ''
  editFormData.handleTimeEnd = planData.value.handleTimeEnd || ''
  editFormData.handleTimeNote = planData.value.handleTimeNote || ''
  editFormData.transportation = planData.value.transportation
  editFormData.transportationNote = planData.value.transportationNote || ''
  editFormData.companionUserId = planData.value.companionUserId ?? null
  editFormData.status = planData.value.status

  await loadFamilyMembers()
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || !planData.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submittingEdit.value = true
      try {
        const currentMaterials = allMaterials.value.map(m => ({
          name: m.name,
          description: m.description,
          orderIndex: m.orderIndex
        }))

        await companionPlanApi.update(planData.value.id, {
          title: editFormData.title,
          handleLocation: editFormData.handleLocation,
          handleTimeStart: editFormData.handleTimeStart || null,
          handleTimeEnd: editFormData.handleTimeEnd || null,
          handleTimeNote: editFormData.handleTimeNote || null,
          transportation: (editFormData.transportation as CompanionPlan['transportation']) || null,
          transportationNote: editFormData.transportationNote || null,
          companionUserId: editFormData.companionUserId,
          status: editFormData.status,
          materials: currentMaterials
        })
        ElMessage.success('陪办计划已更新！')
        editDialogVisible.value = false
        loadPlan()
      } catch (error) {
        console.error('Edit plan error:', error)
      } finally {
        submittingEdit.value = false
      }
    }
  })
}

const addMaterialDialogVisible = ref(false)
const addMaterialFormRef = ref<FormInstance>()
const addMaterialFormData = reactive({
  name: '',
  description: ''
})

const addMaterialFormRules: FormRules = {
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' }
  ]
}

const openAddMaterialDialog = () => {
  addMaterialFormData.name = ''
  addMaterialFormData.description = ''
  addMaterialDialogVisible.value = true
}

const handleAddMaterial = async () => {
  if (!addMaterialFormRef.value || !planData.value) return

  await addMaterialFormRef.value.validate(async (valid) => {
    if (valid) {
      submittingMaterial.value = true
      try {
        const currentMaterials = allMaterials.value.map(m => ({
          name: m.name,
          description: m.description,
          orderIndex: m.orderIndex
        }))
        currentMaterials.push({
          name: addMaterialFormData.name,
          description: addMaterialFormData.description || null,
          orderIndex: allMaterials.value.length
        })

        await companionPlanApi.update(planData.value.id, {
          materials: currentMaterials
        })
        ElMessage.success('材料已添加！')
        addMaterialDialogVisible.value = false
        loadPlan()
      } catch (error) {
        console.error('Add material error:', error)
      } finally {
        submittingMaterial.value = false
      }
    }
  })
}

onMounted(async () => {
  await loadPlan()
})
</script>

<style scoped>
.elderly-view {
  max-width: 900px;
  margin: 0 auto;
}

.elderly-back-btn {
  height: 64px !important;
  padding: 12px 28px !important;
  font-size: 20px !important;
}

.elderly-info-card {
  background: linear-gradient(135deg, #FFF9F0 0%, #FFFFFF 100%);
}

.elderly-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.elderly-info-label {
  color: var(--color-text-secondary);
  font-weight: 500;
  min-width: 120px;
}

.elderly-info-value {
  color: var(--color-text-primary);
}

.elderly-time-box {
  background-color: rgba(255, 122, 69, 0.1);
  border-radius: 16px;
  padding: 24px;
  border-left: 6px solid var(--color-primary);
}

.material-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent !important;
}

.material-card:hover {
  border-color: var(--color-primary-light) !important;
  transform: translateY(-2px);
}

.material-prepared {
  background-color: rgba(82, 196, 26, 0.05) !important;
  border-color: rgba(82, 196, 26, 0.3) !important;
}

.elderly-checkbox :deep(.el-checkbox__inner) {
  width: 32px !important;
  height: 32px !important;
  border-radius: 8px !important;
}

.elderly-checkbox :deep(.el-checkbox__inner::after) {
  height: 18px !important;
  left: 11px !important;
  width: 8px !important;
}

.elderly-checkbox :deep(.el-checkbox__label) {
  font-size: 20px !important;
  padding-left: 12px !important;
}

.confirmation-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent !important;
}

.confirmation-card:hover {
  border-color: var(--color-primary-light) !important;
}

.needs-companion {
  background-color: rgba(82, 196, 26, 0.05) !important;
  border-color: rgba(82, 196, 26, 0.3) !important;
}

.elderly-textarea :deep(.el-textarea__inner) {
  font-size: 20px !important;
  line-height: 1.8 !important;
  padding: 20px !important;
  min-height: 160px !important;
}

.elderly-save-btn {
  height: 80px !important;
  font-size: 24px !important;
  padding: 16px 48px !important;
  border-radius: 16px !important;
  font-weight: 700 !important;
}

.status-item {
  text-align: center;
  padding: 32px 24px;
  background-color: #FAFAFA;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.status-item:hover {
  background-color: #F5F5F5;
}

.status-confirmed {
  background-color: rgba(82, 196, 26, 0.08);
  border: 2px solid rgba(82, 196, 26, 0.2);
}

.concerns-box {
  background-color: #FFFBF5;
  border-radius: 12px;
  padding: 24px;
}

.desc-label {
  font-size: 16px !important;
  font-weight: 600 !important;
  background-color: #FFF9F0 !important;
}

:deep(.el-descriptions__label) {
  width: 140px !important;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__cell) {
  padding: 20px 24px !important;
}

.line-through {
  text-decoration: line-through;
}

@media (max-width: 768px) {
  .elderly-info-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .elderly-save-btn {
    width: 100%;
  }
}
</style>
