<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>🗓️</span>
      <span>收听日程</span>
      <el-button
        v-if="userStore.user?.role !== 'elderly'"
        type="primary"
        size="large"
        class="ml-auto"
        @click="openCreateDialog"
      >
        ➕ 新建收听日程
      </el-button>
    </h1>

    <el-row :gutter="16" class="mb-6">
      <el-col :xs="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <span class="stat-icon">📋</span>
            <div class="stat-content">
              <div class="stat-value">{{ stats?.totalSchedules || 0 }}</div>
              <div class="stat-label">日程总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <span class="stat-icon">⏰</span>
            <div class="stat-content">
              <div class="stat-value">{{ stats?.todayPending || 0 }}</div>
              <div class="stat-label">今日待收听</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <span class="stat-icon">✅</span>
            <div class="stat-content">
              <div class="stat-value">{{ completionRate }}%</div>
              <div class="stat-label">收听完成率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <span class="stat-icon">⚠️</span>
            <div class="stat-content">
              <div class="stat-value">{{ stats?.consecutiveSkipped?.length || 0 }}</div>
              <div class="stat-label">连续跳过栏目</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" type="card" size="large" class="mb-6">
      <el-tab-pane label="📅 今日待收听" name="today" />
      <el-tab-pane label="📆 本周收听" name="week" />
      <el-tab-pane label="📋 日程管理" name="schedules" />
      <el-tab-pane label="🗓️ 日历视图" name="calendar" />
    </el-tabs>

    <div v-if="activeTab === 'today'">
      <div v-if="loadingToday" class="loading-container py-16">
        <div class="text-gray-500 text-lg">⏳ 加载中...</div>
      </div>
      <div v-else-if="todayRecords.length === 0" class="loading-container py-16">
        <el-empty description="今日暂无收听安排" />
      </div>
      <div v-else class="space-y-4">
        <el-card
          v-for="record in todayRecordsSorted"
          :key="record.id"
          class="record-card shadow-card-hover"
          :body-style="{ padding: '20px' }"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-xl font-semibold line-clamp-1">
                  {{ record.schedule?.programName || '未知节目' }}
                </h3>
                <el-tag :type="getStatusType(record.status)" size="large" effect="dark">
                  {{ record.statusDisplay }}
                </el-tag>
              </div>
              <div class="space-y-1 text-base text-gray-600">
                <div class="flex items-center gap-2">
                  <span>🕐</span>
                  <span>{{ record.schedule?.broadcastTime }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>📡</span>
                  <span>{{ record.schedule?.channelSource }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>👤</span>
                  <span>{{ record.listenerName }}</span>
                </div>
                <div v-if="record.schedule?.remark" class="flex items-center gap-2">
                  <span>📝</span>
                  <span>{{ record.schedule.remark }}</span>
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-2 ml-4">
              <template v-if="record.status === 'pending'">
                <el-button type="success" size="large" @click="handleUpdateStatus(record, 'listened')">
                  ✅ 已收听
                </el-button>
                <el-button type="warning" size="large" @click="handleUpdateStatus(record, 'skipped')">
                  ⏭️ 跳过
                </el-button>
                <el-button type="primary" size="large" @click="handleWantExcerpt(record)">
                  📝 想补记摘录
                </el-button>
              </template>
              <template v-else-if="record.status === 'want_excerpt'">
                <el-button
                  type="primary"
                  size="large"
                  @click="goToDraft(record.excerptDraftId)"
                >
                  ✏️ 去补记摘录
                </el-button>
              </template>
              <template v-else>
                <el-button size="large" @click="handleUpdateStatus(record, 'pending')">
                  🔄 重置状态
                </el-button>
              </template>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div v-if="activeTab === 'week'">
      <div v-if="loadingWeek" class="loading-container py-16">
        <div class="text-gray-500 text-lg">⏳ 加载中...</div>
      </div>
      <div v-else-if="weekRecords.length === 0" class="loading-container py-16">
        <el-empty description="本周暂无收听安排" />
      </div>
      <div v-else class="space-y-6">
        <div v-for="(dayRecords, date) in weekRecordsByDate" :key="date" class="week-day-section">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-lg font-semibold text-primary">📅 {{ formatDateLabel(date) }}</span>
            <el-tag size="large" type="info">
              {{ dayRecords.filter(r => r.status === 'listened').length }}/{{ dayRecords.length }} 已收听
            </el-tag>
          </div>
          <div class="space-y-3">
            <el-card
              v-for="record in dayRecords"
              :key="record.id"
              class="record-card shadow-card-hover"
              :body-style="{ padding: '16px' }"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold">{{ record.schedule?.programName }}</span>
                    <el-tag :type="getStatusType(record.status)" size="small" effect="dark">
                      {{ record.statusDisplay }}
                    </el-tag>
                  </div>
                  <div class="text-sm text-gray-500">
                    🕐 {{ record.schedule?.broadcastTime }} · 📡 {{ record.schedule?.channelSource }} · 👤 {{ record.listenerName }}
                  </div>
                </div>
                <div class="flex gap-1 ml-2" v-if="record.status === 'pending'">
                  <el-button type="success" size="small" @click="handleUpdateStatus(record, 'listened')">✅</el-button>
                  <el-button type="warning" size="small" @click="handleUpdateStatus(record, 'skipped')">⏭️</el-button>
                  <el-button type="primary" size="small" @click="handleWantExcerpt(record)">📝</el-button>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'schedules'">
      <div v-if="loadingSchedules" class="loading-container py-16">
        <div class="text-gray-500 text-lg">⏳ 加载中...</div>
      </div>
      <div v-else-if="schedules.length === 0" class="loading-container py-16">
        <el-empty description="暂无收听日程，点击右上角创建第一个日程吧！" />
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-card
          v-for="schedule in schedules"
          :key="schedule.id"
          class="schedule-card shadow-card-hover"
          :body-style="{ padding: '20px' }"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h3 class="text-xl font-semibold line-clamp-1">{{ schedule.programName }}</h3>
              <p class="text-sm text-gray-500 mt-1">
                创建人：{{ schedule.createdByName }} · {{ formatDate(schedule.createdAt) }}
              </p>
            </div>
            <el-tag :type="schedule.isActive ? 'success' : 'info'" size="large" effect="dark">
              {{ schedule.isActive ? '启用中' : '已停用' }}
            </el-tag>
          </div>

          <div class="space-y-2 mb-3">
            <div class="flex items-center gap-2 text-base text-gray-600">
              <span>🕐</span>
              <span>{{ schedule.broadcastTime }}</span>
            </div>
            <div class="flex items-center gap-2 text-base text-gray-600">
              <span>📡</span>
              <span>{{ schedule.channelSource }}</span>
            </div>
            <div class="flex items-center gap-2 text-base text-gray-600">
              <span>🔄</span>
              <span>{{ schedule.repeatCycleDisplay }}</span>
            </div>
            <div class="flex items-center gap-2 text-base text-gray-600">
              <span>⏰</span>
              <span>提前 {{ schedule.reminderAdvanceMinutes }} 分钟提醒</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 mb-3">
            <el-tag
              v-for="listener in schedule.suitableListeners"
              :key="listener.id"
              size="large"
              type="warning"
            >
              👤 {{ listener.firstName }}{{ listener.lastName }}
            </el-tag>
          </div>

          <div v-if="schedule.remark" class="text-sm text-gray-500 mb-3">
            📝 {{ schedule.remark }}
          </div>

          <el-divider class="my-2" />

          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">今日 {{ schedule.recordCountToday }} 条记录</span>
            <div class="flex items-center gap-1" v-if="userStore.user?.role !== 'elderly'">
              <el-button type="primary" link size="small" @click="openEditDialog(schedule)">
                ✏️ 编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteSchedule(schedule)">
                🗑️ 删除
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div v-if="activeTab === 'calendar'">
      <el-card shadow="hover" :body-style="{ padding: '20px' }">
        <el-calendar v-model="calendarDate" ref="calendarRef">
          <template #date-cell="{ data }">
            <div class="calendar-cell">
              <div class="calendar-day">{{ data.day.split('-').slice(-1)[0] }}</div>
              <div v-if="getCalendarDayRecords(data.day).length > 0" class="calendar-dots">
                <el-tooltip
                  v-for="(record, idx) in getCalendarDayRecords(data.day).slice(0, 3)"
                  :key="idx"
                  :content="`${record.schedule?.programName} - ${record.statusDisplay}`"
                  placement="top"
                >
                  <span class="calendar-dot" :class="`dot-${record.status}`" />
                </el-tooltip>
                <span
                  v-if="getCalendarDayRecords(data.day).length > 3"
                  class="text-xs text-gray-500"
                >
                  +{{ getCalendarDayRecords(data.day).length - 3 }}
                </span>
              </div>
            </div>
          </template>
        </el-calendar>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '✏️ 编辑收听日程' : '📋 新建收听日程'"
      width="700px"
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
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="栏目名称" prop="programName">
              <el-input
                v-model="formData.programName"
                placeholder="请输入广播栏目名称，例如：新闻和报纸摘要"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="播出日期" prop="startDate">
              <el-date-picker
                v-model="formData.startDate"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期（可选）">
              <el-date-picker
                v-model="formData.endDate"
                type="date"
                placeholder="选择结束日期，留空表示长期有效"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="重复周期" prop="repeatCycle">
              <el-select v-model="formData.repeatCycle" placeholder="请选择重复周期" style="width: 100%">
                <el-option label="仅一次" value="once" />
                <el-option label="每天" value="daily" />
                <el-option label="工作日（周一至周五）" value="weekdays" />
                <el-option label="周末（周六至周日）" value="weekends" />
                <el-option label="每周" value="weekly" />
                <el-option label="每两周" value="biweekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="播出时段" prop="broadcastTime">
              <el-time-picker
                v-model="formData.broadcastTime"
                placeholder="选择播出时间"
                value-format="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item
          v-if="formData.repeatCycle === 'weekly' || formData.repeatCycle === 'biweekly'"
          label="选择星期"
        >
          <el-checkbox-group v-model="weekdaySelections">
            <el-checkbox label="0">周一</el-checkbox>
            <el-checkbox label="1">周二</el-checkbox>
            <el-checkbox label="2">周三</el-checkbox>
            <el-checkbox label="3">周四</el-checkbox>
            <el-checkbox label="4">周五</el-checkbox>
            <el-checkbox label="5">周六</el-checkbox>
            <el-checkbox label="6">周日</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="频道来源" prop="channelSource">
              <el-input
                v-model="formData.channelSource"
                placeholder="请输入频道，例如：中央人民广播电台中国之声"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="提醒提前量（分钟）">
              <el-input-number
                v-model="formData.reminderAdvanceMinutes"
                :min="0"
                :max="120"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="适合收听人" prop="suitableListenerIds">
          <el-select
            v-model="formData.suitableListenerIds"
            multiple
            placeholder="请选择适合收听的家人"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="member in familyMembers"
              :key="member.id"
              :label="`${member.firstName}${member.lastName} (${member.roleDisplay})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="2"
            placeholder="例如：这个栏目对了解国家大事很有帮助，记得认真听"
          />
        </el-form-item>

        <el-form-item v-if="isEditing" label="是否启用">
          <el-switch v-model="formData.isActive" />
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
          {{ isEditing ? '保存修改' : '创建日程' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="excerptNoteDialogVisible"
      title="📝 想补记摘录"
      width="500px"
      size="large"
    >
      <p class="mb-4 text-gray-600">
        系统将为「{{ currentRecord?.schedule?.programName }}」生成一份节目摘录草稿，您可以稍后在节目摘录页继续补全内容。
      </p>
      <el-form label-position="top" size="large">
        <el-form-item label="补充说明（可选）">
          <el-input
            v-model="excerptNote"
            type="textarea"
            :rows="3"
            placeholder="记录一下想摘录的重点内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button size="large" @click="excerptNoteDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submittingStatus"
          @click="confirmWantExcerpt"
        >
          ✅ 生成草稿
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
import type {
  ListeningSchedule,
  ListeningRecord,
  ListeningScheduleStats,
  ListeningStatus,
  FamilyMember
} from '@/types'
import { scheduleApi, recordApi, familyApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loadingToday = ref(false)
const loadingWeek = ref(false)
const loadingSchedules = ref(false)
const submitting = ref(false)
const submittingStatus = ref(false)
const activeTab = ref('today')
const stats = ref<ListeningScheduleStats | null>(null)
const todayRecords = ref<ListeningRecord[]>([])
const weekRecords = ref<ListeningRecord[]>([])
const schedules = ref<ListeningSchedule[]>([])
const familyMembers = ref<FamilyMember[]>([])
const calendarDate = ref(new Date())
const calendarRef = ref()

const todayRecordsSorted = computed(() => {
  return [...todayRecords.value].sort((a, b) => {
    const timeA = a.schedule?.broadcastTime || '00:00'
    const timeB = b.schedule?.broadcastTime || '00:00'
    return timeA.localeCompare(timeB)
  })
})

const weekRecordsByDate = computed(() => {
  const grouped: Record<string, ListeningRecord[]> = {}
  weekRecords.value.forEach(record => {
    const date = record.listenDate
    if (!grouped[date]) grouped[date] = []
    grouped[date].push(record)
  })
  Object.keys(grouped).forEach(date => {
    grouped[date].sort((a, b) => {
      const timeA = a.schedule?.broadcastTime || '00:00'
      const timeB = b.schedule?.broadcastTime || '00:00'
      return timeA.localeCompare(timeB)
    })
  })
  return grouped
})

const completionRate = computed(() => {
  if (!stats.value) return 0
  return Math.round(stats.value.completionRate * 100)
})

const weekdaySelections = ref<string[]>([])

const dialogVisible = ref(false)
const excerptNoteDialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const currentRecord = ref<ListeningRecord | null>(null)
const excerptNote = ref('')

const formData = reactive({
  programName: '',
  startDate: '',
  endDate: null as string | null,
  repeatCycle: 'daily' as ListeningSchedule['repeatCycle'],
  repeatWeekdays: null as string | null,
  broadcastTime: '',
  channelSource: '',
  reminderAdvanceMinutes: 10,
  suitableListenerIds: [] as number[],
  remark: null as string | null,
  isActive: true
})

const formRules: FormRules = {
  programName: [
    { required: true, message: '请输入栏目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择播出日期', trigger: 'change' }
  ],
  repeatCycle: [
    { required: true, message: '请选择重复周期', trigger: 'change' }
  ],
  broadcastTime: [
    { required: true, message: '请选择播出时段', trigger: 'change' }
  ],
  channelSource: [
    { required: true, message: '请输入频道来源', trigger: 'blur' }
  ],
  suitableListenerIds: [
    { required: true, message: '请选择适合收听人', trigger: 'change', type: 'array' }
  ]
}

const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'danger' | 'primary' => {
  switch (status) {
    case 'listened':
      return 'success'
    case 'skipped':
      return 'warning'
    case 'want_excerpt':
      return 'primary'
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

const formatDateLabel = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(today.getDate() + 1)
  const isToday = date.toDateString() === today.toDateString()
  const isTomorrow = date.toDateString() === tomorrow.toDateString()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekday = weekdays[date.getDay()]
  const base = date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  if (isToday) return `今天 ${base} ${weekday}`
  if (isTomorrow) return `明天 ${base} ${weekday}`
  return `${base} ${weekday}`
}

const getCalendarDayRecords = (dateStr: string) => {
  return weekRecords.value.filter(r => r.listenDate === dateStr)
}

const resetForm = () => {
  formData.programName = ''
  formData.startDate = new Date().toISOString().split('T')[0]
  formData.endDate = null
  formData.repeatCycle = 'daily'
  formData.repeatWeekdays = null
  formData.broadcastTime = '07:00'
  formData.channelSource = ''
  formData.reminderAdvanceMinutes = 10
  formData.suitableListenerIds = []
  formData.remark = null
  formData.isActive = true
  weekdaySelections.value = []
}

const loadStats = async () => {
  try {
    stats.value = await scheduleApi.getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadTodayRecords = async () => {
  loadingToday.value = true
  try {
    todayRecords.value = await recordApi.getToday()
  } catch (error) {
    console.error('Failed to load today records:', error)
  } finally {
    loadingToday.value = false
  }
}

const loadWeekRecords = async () => {
  loadingWeek.value = true
  try {
    const today = new Date()
    const weekStart = new Date(today)
    const weekEnd = new Date(today)
    weekStart.setDate(today.getDate() - today.getDay() + 1)
    weekEnd.setDate(weekStart.getDate() + 6)
    const format = (d: Date) => d.toISOString().split('T')[0]
    weekRecords.value = await recordApi.getRange(format(weekStart), format(weekEnd))
  } catch (error) {
    console.error('Failed to load week records:', error)
  } finally {
    loadingWeek.value = false
  }
}

const loadSchedules = async () => {
  loadingSchedules.value = true
  try {
    schedules.value = await scheduleApi.getList()
  } catch (error) {
    console.error('Failed to load schedules:', error)
  } finally {
    loadingSchedules.value = false
  }
}

const loadFamilyMembers = async () => {
  try {
    familyMembers.value = await familyApi.getMembers()
  } catch (error) {
    console.error('Failed to load family members:', error)
  }
}

const refreshAll = async () => {
  await Promise.all([loadStats(), loadTodayRecords(), loadWeekRecords(), loadSchedules()])
}

const openCreateDialog = async () => {
  isEditing.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
  await loadFamilyMembers()
}

const openEditDialog = async (schedule: ListeningSchedule) => {
  isEditing.value = true
  editingId.value = schedule.id
  resetForm()

  formData.programName = schedule.programName
  formData.startDate = schedule.startDate
  formData.endDate = schedule.endDate
  formData.repeatCycle = schedule.repeatCycle
  formData.repeatWeekdays = schedule.repeatWeekdays
  formData.broadcastTime = schedule.broadcastTime
  formData.channelSource = schedule.channelSource
  formData.reminderAdvanceMinutes = schedule.reminderAdvanceMinutes
  formData.suitableListenerIds = schedule.suitableListenerIds || schedule.suitableListeners.map(l => l.id)
  formData.remark = schedule.remark
  formData.isActive = schedule.isActive

  if (schedule.repeatWeekdays) {
    weekdaySelections.value = schedule.repeatWeekdays.split(',')
  }

  dialogVisible.value = true
  await loadFamilyMembers()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        let repeatWeekdays: string | null = null
        if ((formData.repeatCycle === 'weekly' || formData.repeatCycle === 'biweekly') && weekdaySelections.value.length > 0) {
          repeatWeekdays = weekdaySelections.value.join(',')
        }

        const payload = {
          programName: formData.programName,
          startDate: formData.startDate,
          endDate: formData.endDate,
          repeatCycle: formData.repeatCycle,
          repeatWeekdays,
          broadcastTime: formData.broadcastTime,
          channelSource: formData.channelSource,
          reminderAdvanceMinutes: formData.reminderAdvanceMinutes,
          suitableListenerIds: formData.suitableListenerIds,
          remark: formData.remark,
          isActive: formData.isActive
        }

        if (isEditing.value && editingId.value) {
          await scheduleApi.update(editingId.value, payload)
          ElMessage.success('收听日程更新成功！')
        } else {
          await scheduleApi.create(payload)
          ElMessage.success('收听日程创建成功！')
        }

        dialogVisible.value = false
        refreshAll()
      } catch (error) {
        console.error('Submit error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDeleteSchedule = async (schedule: ListeningSchedule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除收听日程「${schedule.programName}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await scheduleApi.remove(schedule.id)
    ElMessage.success('删除成功')
    refreshAll()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
    }
  }
}

const handleUpdateStatus = async (record: ListeningRecord, newStatus: ListeningStatus) => {
  submittingStatus.value = true
  try {
    await recordApi.updateStatus(record.id, { newStatus })
    ElMessage.success('状态更新成功')
    refreshAll()
  } catch (error) {
    console.error('Update status error:', error)
  } finally {
    submittingStatus.value = false
  }
}

const handleWantExcerpt = (record: ListeningRecord) => {
  currentRecord.value = record
  excerptNote.value = ''
  excerptNoteDialogVisible.value = true
}

const confirmWantExcerpt = async () => {
  if (!currentRecord.value) return
  submittingStatus.value = true
  try {
    const result = await recordApi.updateStatus(currentRecord.value.id, {
      newStatus: 'want_excerpt',
      note: excerptNote.value || null,
      generateExcerpt: true
    })
    ElMessage.success('已生成摘录草稿')
    excerptNoteDialogVisible.value = false
    if (result.excerptDraftId) {
      goToDraft(result.excerptDraftId)
    } else {
      refreshAll()
    }
  } catch (error) {
    console.error('Want excerpt error:', error)
  } finally {
    submittingStatus.value = false
  }
}

const goToDraft = (draftId: number | null) => {
  if (!draftId) return
  router.push({ path: '/', query: { draftId: draftId.toString() } })
}

watch(activeTab, (newTab) => {
  if (newTab === 'today') loadTodayRecords()
  else if (newTab === 'week') loadWeekRecords()
  else if (newTab === 'schedules') loadSchedules()
})

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #e67e22;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 4px;
}

.record-card :deep(.el-card__body),
.schedule-card :deep(.el-card__body) {
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

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.ml-4 {
  margin-left: 1rem;
}

.week-day-section {
  padding: 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #fed7aa;
}

.calendar-cell {
  min-height: 80px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.calendar-day {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.calendar-dots {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-wrap: wrap;
}

.calendar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-pending {
  background-color: #909399;
}

.dot-listened {
  background-color: #67c23a;
}

.dot-skipped {
  background-color: #e6a23c;
}

.dot-want_excerpt {
  background-color: #409eff;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.flex {
  display: flex;
}

.flex-wrap {
  flex-wrap: wrap;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.items-start {
  align-items: flex-start;
}

.justify-between {
  justify-content: space-between;
}

.gap-1 {
  gap: 0.25rem;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 0.75rem;
}

.flex-1 {
  flex: 1;
}

.min-w-0 {
  min-width: 0;
}

.flex-shrink-0 {
  flex-shrink: 0;
}
</style>
