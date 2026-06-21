<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>👨‍👩‍👧‍👦</span>
      <span>家庭共享</span>
    </h1>

    <el-row :gutter="24">
      <el-col :xs="24" :lg="8">
        <div class="form-section">
          <h2 class="section-title">👥 家庭成员</h2>
          <div v-if="loadingMembers" class="loading-container py-8">
            <div class="text-gray-500 text-lg">⏳ 加载中...</div>
          </div>
          <div v-else-if="members.length === 0" class="py-8">
            <el-empty description="暂无家庭成员" />
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="member in membersWithCount"
              :key="member.id"
              class="flex items-center gap-4 p-4 bg-orange-50 rounded-xl"
            >
              <div class="member-avatar text-3xl">
                {{ member.avatar }}
              </div>
              <div class="flex-1">
                <p class="text-lg font-semibold">{{ member.firstName || member.username }}</p>
                <p class="text-sm text-gray-500">
                  {{ member.role === 'elderly' ? '长辈' : member.role === 'admin' ? '管理员' : '家人' }}
                  <span class="ml-2">·</span>
                  <span class="ml-2">{{ member.roleDisplay }}</span>
                </p>
              </div>
              <el-tag type="primary" size="large">
                {{ member.contributionCount || 0 }} 条记录
              </el-tag>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="16">
        <div class="form-section">
          <h2 class="section-title">📜 家庭时间线</h2>

          <div v-if="loadingFeed" class="loading-container py-8">
            <div class="text-gray-500 text-lg">⏳ 加载中...</div>
          </div>

          <div v-else-if="feedItems.length === 0" class="py-8">
            <el-empty description="暂无动态，快去记录第一条节目吧！" />
          </div>

          <div v-else class="timeline">
            <div
              v-for="(item, idx) in feedItems"
              :key="`${item.type}-${idx}`"
              class="timeline-item"
            >
              <el-card
                v-if="item.type === 'excerpt'"
                class="shadow-card-hover"
                :body-style="{ padding: '20px' }"
              >
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <span class="text-3xl">{{ getMemberAvatar((item.data as ProgramExcerpt).createdBy?.id) }}</span>
                      <div>
                        <h3 class="text-xl font-semibold">{{ (item.data as ProgramExcerpt).programName }}</h3>
                        <p class="text-sm text-gray-500">
                          <span class="font-medium">{{ getMemberName((item.data as ProgramExcerpt).createdBy?.id) }}</span>
                          <span class="mx-2">·</span>
                          📅 {{ (item.data as ProgramExcerpt).date }} · ⏰ {{ (item.data as ProgramExcerpt).timeSlot }}
                        </p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <el-tag
                        :type="confirmationTagType((item.data as ProgramExcerpt).confirmationStatus)"
                        size="large"
                        effect="light"
                      >
                        {{ confirmationLabel((item.data as ProgramExcerpt).confirmationStatus) }}
                      </el-tag>
                      <el-tag
                        v-if="(item.data as ProgramExcerpt).topic"
                        :style="{ backgroundColor: (item.data as ProgramExcerpt).topic!.color + '20', color: (item.data as ProgramExcerpt).topic!.color }"
                        size="large"
                      >
                        {{ (item.data as ProgramExcerpt).topic!.icon }} {{ (item.data as ProgramExcerpt).topic!.name }}
                      </el-tag>
                      <el-tag
                        v-if="(item.data as ProgramExcerpt).isDuplicate"
                        type="warning"
                        size="large"
                      >
                        ⚠️ 重复
                      </el-tag>
                    </div>
                  </div>

                  <div class="text-base text-gray-700">
                    <span class="font-medium">📝 内容摘要：</span>
                    {{ (item.data as ProgramExcerpt).contentSummary }}
                  </div>

                  <div
                    v-if="(item.data as ProgramExcerpt).elderlyNotes"
                    class="bg-elderly rounded-lg p-4"
                  >
                    <div class="flex items-center gap-2 mb-2">
                      <span class="text-xl">👴</span>
                      <span class="font-semibold text-primary">老人补充</span>
                    </div>
                    <p class="text-lg text-gray-800">{{ (item.data as ProgramExcerpt).elderlyNotes }}</p>
                  </div>

                  <div
                    v-if="(item as any).confirmationInfo"
                    class="p-3 rounded-lg border-l-4"
                    :class="(item as any).confirmationInfo.confirmationStatus === 'confirmed' ? 'bg-green-50 border-green-400' : 'bg-orange-50 border-orange-400'"
                  >
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-medium text-sm">
                        {{ (item as any).confirmationInfo.confirmationStatus === 'confirmed' ? '✅ 已确认' : '❗ 需核实' }}
                      </span>
                      <span class="text-sm text-gray-500">
                        确认人：{{ (item as any).confirmationInfo.confirmedByName }}
                      </span>
                      <span class="text-sm text-gray-400">
                        · {{ formatTime((item as any).confirmationInfo.confirmedAt) }}
                      </span>
                    </div>
                    <p v-if="(item as any).confirmationInfo.confirmationNote" class="text-sm text-gray-600 mt-1">
                      备注：{{ (item as any).confirmationInfo.confirmationNote.length > 50 ? (item as any).confirmationInfo.confirmationNote.slice(0, 50) + '...' : (item as any).confirmationInfo.confirmationNote }}
                    </p>
                  </div>

                  <el-divider class="my-3" />

                  <div>
                    <div class="flex items-center justify-between mb-3">
                      <h4 class="text-lg font-semibold">💬 评论 ({{ commentsMap[(item.data as ProgramExcerpt).id]?.length || 0 }})</h4>
                      <el-button
                        type="primary"
                        size="large"
                        @click="openCommentDialog(item.data as ProgramExcerpt)"
                      >
                        ✏️ 发表评论
                      </el-button>
                    </div>

                    <div v-if="loadingComments[(item.data as ProgramExcerpt).id]" class="py-4 text-center text-gray-500">
                      加载评论中...
                    </div>

                    <div v-else-if="commentsMap[(item.data as ProgramExcerpt).id]?.length > 0" class="space-y-3">
                      <div
                        v-for="comment in commentsMap[(item.data as ProgramExcerpt).id]"
                        :key="comment.id"
                        class="flex gap-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <div class="text-2xl">
                          {{ comment.user?.avatar || '👤' }}
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center gap-2 mb-1">
                            <span class="font-medium">{{ comment.user?.firstName || comment.user?.username || '未知用户' }}</span>
                            <span class="text-xs text-gray-400">{{ formatTime(comment.createdAt) }}</span>
                          </div>
                          <p class="text-base text-gray-700">{{ comment.content }}</p>
                        </div>
                      </div>
                    </div>

                    <div v-else class="text-center py-4 text-gray-400">
                      暂无评论，快来抢沙发吧！
                    </div>
                  </div>
                </div>
              </el-card>

              <el-card
                v-else-if="item.type === 'review_package'"
                class="shadow-card-hover cursor-pointer"
                :body-style="{ padding: '20px' }"
                @click="router.push(`/review-packages/${(item.data as ReviewPackage).id}`)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-3">
                    <span class="text-4xl">📚</span>
                    <div>
                      <div class="flex items-center gap-2 mb-1">
                        <h3 class="text-xl font-semibold">{{ (item.data as ReviewPackage).title }}</h3>
                        <el-tag type="primary" size="large" effect="light">资料包</el-tag>
                      </div>
                      <p class="text-sm text-gray-500">
                        <span class="font-medium">{{ (item.data as ReviewPackage).createdByName }}</span>
                        <span class="mx-2">·</span>
                        📅 {{ formatTime((item.data as ReviewPackage).createdAt) }}
                      </p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <el-tag size="large" type="info">
                      📄 {{ (item.data as ReviewPackage).itemCount }} 条内容
                    </el-tag>
                    <el-tag size="large" type="success">
                      💬 {{ (item.data as ReviewPackage).feedbackCount }} 条反馈
                    </el-tag>
                  </div>
                </div>
                <div v-if="(item.data as ReviewPackage).purposeDescription" class="mt-3 text-base text-gray-600 line-clamp-2">
                  📌 {{ (item.data as ReviewPackage).purposeDescription }}
                </div>
                <div v-if="(item.data as ReviewPackage).guideText" class="mt-3 p-3 bg-orange-50 rounded-lg">
                  <span class="text-sm text-orange-600">💬 {{ (item.data as ReviewPackage).guideText }}</span>
                </div>
                <p class="mt-3 text-sm text-primary font-medium">点击查看详情 →</p>
              </el-card>

              <el-card
                v-else-if="item.type === 'review_package_feedback'"
                class="shadow-card-hover cursor-pointer"
                :body-style="{ padding: '20px' }"
                @click="router.push(`/review-packages/${(item.data as ReviewPackageFeedItem).packageId}`)"
              >
                <div class="flex items-start gap-3">
                  <span class="text-3xl">{{ (item.data as ReviewPackageFeedItem).elderlyUserAvatar || '👴' }}</span>
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <h3 class="text-lg font-semibold">{{ (item.data as ReviewPackageFeedItem).elderlyUserName }}</h3>
                      <el-tag
                        size="large"
                        effect="light"
                        :type="feedbackTagType((item.data as ReviewPackageFeedItem).feedbackType)"
                      >
                        {{ feedbackIcon((item.data as ReviewPackageFeedItem).feedbackType) }} {{ (item.data as ReviewPackageFeedItem).feedbackTypeDisplay }}
                      </el-tag>
                      <span class="text-sm text-gray-500">
                        {{ formatTime(item.createdAt) }}
                      </span>
                    </div>
                    <p class="text-base text-gray-700 mb-2">
                      对资料包「<span class="font-medium text-primary">{{ (item.data as ReviewPackageFeedItem).packageTitle }}</span>」中的内容进行了反馈
                    </p>
                    <div class="p-3 bg-gray-50 rounded-lg">
                      <p class="text-sm font-medium text-gray-700 mb-1">📻 {{ (item.data as ReviewPackageFeedItem).excerptProgramName }}</p>
                      <p class="text-sm text-gray-600 line-clamp-1">{{ (item.data as ReviewPackageFeedItem).excerptContentSummary }}</p>
                    </div>
                    <p v-if="(item.data as ReviewPackageFeedItem).note" class="mt-2 text-sm text-gray-600 p-2 bg-orange-50 rounded">
                      💭 {{ (item.data as ReviewPackageFeedItem).note }}
                    </p>
                  </div>
                </div>
              </el-card>

              <el-card
                v-else-if="item.type === 'companion_plan'"
                class="shadow-card-hover cursor-pointer"
                :body-style="{ padding: '20px' }"
                @click="router.push(`/companion-plans/${(item.data as CompanionPlan).id}`)"
              >
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <span class="text-3xl">🤝</span>
                      <div>
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="text-xl font-semibold">{{ (item.data as CompanionPlan).title }}</h3>
                          <el-tag
                            size="large"
                            effect="light"
                            :type="companionPlanStatusTagType((item.data as CompanionPlan).status)"
                          >
                            {{ companionPlanStatusLabel((item.data as CompanionPlan).status) }}
                          </el-tag>
                        </div>
                        <p class="text-sm text-gray-500">
                          <span class="font-medium">{{ (item.data as CompanionPlan).createdByName }}</span>
                          <span class="mx-2">·</span>
                          📅 {{ formatTime(item.createdAt) }}
                        </p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <el-tag
                        size="large"
                        type="primary"
                        effect="light"
                      >
                        {{ companionPlanSourceTypeLabel((item.data as CompanionPlan).sourceType) }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 gap-4">
                    <div class="flex items-center gap-2 text-base text-gray-700">
                      <span>📍</span>
                      <span>办理地点：{{ (item.data as CompanionPlan).handleLocation }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-base text-gray-700">
                      <span>⏰</span>
                      <span>办理时间：{{ formatCompanionPlanTime(item.data as CompanionPlan) }}</span>
                    </div>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-base font-medium text-gray-700">📋 材料准备进度</span>
                      <span class="text-base text-primary font-semibold">
                        {{ (item.data as CompanionPlan).preparedMaterialCount }}/{{ (item.data as CompanionPlan).materialCount }}
                      </span>
                    </div>
                    <el-progress
                      :percentage="Math.round((item.data as CompanionPlan).materialPreparedRate * 100)"
                      :stroke-width="12"
                      color="#f97316"
                    />
                  </div>

                  <div
                    v-if="(item as any).activityInfo"
                    class="p-3 rounded-lg border-l-4 bg-orange-50 border-orange-400"
                  >
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-medium text-sm">
                        🔄 {{ formatCompanionPlanActivity((item as any).activityInfo as CompanionPlanFeedItem) }}
                      </span>
                      <span class="text-sm text-gray-400">
                        · {{ formatTime((item as any).activityInfo.updatedAt) }}
                      </span>
                    </div>
                  </div>

                  <p class="text-sm text-primary font-medium">点击查看详情 →</p>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog
      v-model="commentDialogVisible"
      title="💬 发表评论"
      width="500px"
      size="large"
    >
      <div class="space-y-4">
        <div v-if="currentExcerpt" class="p-4 bg-orange-50 rounded-xl">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-2xl">{{ getMemberAvatar(currentExcerpt.createdBy?.id) }}</span>
            <p class="font-semibold text-lg">{{ currentExcerpt.programName }}</p>
          </div>
          <p class="text-sm text-gray-500 mt-1 line-clamp-2">{{ currentExcerpt.contentSummary }}</p>
        </div>

        <el-form label-position="top" size="large">
          <el-form-item label="评论内容">
            <el-input
              v-model="commentContent"
              type="textarea"
              :rows="4"
              placeholder="写下您的评论..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button size="large" @click="commentDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submittingComment"
          :disabled="!commentContent.trim()"
          @click="handleSubmitComment"
        >
          发表评论
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FamilyMember, ProgramExcerpt, Comment, ConfirmationInfo, FeedItem, ReviewPackage, ReviewPackageFeedItem, CompanionPlan, CompanionPlanFeedItem } from '@/types'
import { familyApi, excerptApi } from '@/api'

const router = useRouter()

const loadingMembers = ref(false)
const loadingFeed = ref(false)
const submittingComment = ref(false)

const members = ref<FamilyMember[]>([])
const feedItems = ref<FeedItem[]>([])

const commentsMap = reactive<Record<number, Comment[]>>({})
const loadingComments = reactive<Record<number, boolean>>({})

const currentExcerpt = ref<ProgramExcerpt | null>(null)
const commentDialogVisible = ref(false)
const commentContent = ref('')

const userMap = reactive<Record<number, FamilyMember>>({})

const membersWithCount = computed(() => {
  return members.value.map(member => {
    let count = 0
    feedItems.value.forEach(item => {
      if (item.type === 'excerpt' && item.data.createdBy?.id === member.id) count++
      if (item.type === 'review_package' && (item.data as ReviewPackage).createdBy?.id === member.id) count++
      if (item.type === 'companion_plan' && (item.data as CompanionPlan).createdBy?.id === member.id) count++
    })
    return {
      ...member,
      contributionCount: count
    }
  })
})

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

const feedbackTagType = (type: string) => {
  const map: Record<string, string> = {
    read: 'success',
    review_again: 'warning',
    needs_explanation: 'danger'
  }
  return map[type] || 'info'
}

const feedbackIcon = (type: string) => {
  const map: Record<string, string> = {
    read: '✅',
    review_again: '🔄',
    needs_explanation: '❓'
  }
  return map[type] || '📝'
}

const companionPlanStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    preparing: 'warning',
    scheduled: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const companionPlanStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '⏳ 待处理',
    preparing: '📋 准备中',
    scheduled: '📅 已安排',
    completed: '✅ 已完成',
    cancelled: '❌ 已取消'
  }
  return map[status] || status
}

const companionPlanSourceTypeLabel = (sourceType: string) => {
  const map: Record<string, string> = {
    excerpt: '📻 节目摘录',
    topic: '📂 主题分类',
    manual: '✍️ 手动创建'
  }
  return map[sourceType] || sourceType
}

const formatCompanionPlanTime = (plan: CompanionPlan) => {
  if (plan.handleTimeStart && plan.handleTimeEnd) {
    const start = new Date(plan.handleTimeStart)
    const end = new Date(plan.handleTimeEnd)
    const startStr = start.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    const endStr = end.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    return `${startStr} - ${endStr}`
  }
  if (plan.handleTimeStart) {
    return new Date(plan.handleTimeStart).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }
  if (plan.handleTimeNote) {
    return plan.handleTimeNote
  }
  return '待定'
}

const formatCompanionPlanActivity = (activity: CompanionPlanFeedItem) => {
  if (activity.materialsConfirmed) {
    return '材料已确认'
  }
  if (activity.timeLocationKnown) {
    return '时间地点已确认'
  }
  if (activity.needsCompanion) {
    return '需要陪同'
  }
  return `状态更新：${activity.statusDisplay}`
}

const getMemberAvatar = (userId?: number) => {
  if (!userId) return '👤'
  return userMap[userId]?.avatar || '👤'
}

const getMemberName = (userId?: number) => {
  if (!userId) return '未知用户'
  const user = userMap[userId]
  return user?.firstName || user?.username || '未知用户'
}

const loadMembers = async () => {
  loadingMembers.value = true
  try {
    members.value = await familyApi.getMembers()
    members.value.forEach(member => {
      userMap[member.id] = member
    })
  } catch (error) {
    console.error('Failed to load members:', error)
  } finally {
    loadingMembers.value = false
  }
}

const loadFeed = async () => {
  loadingFeed.value = true
  try {
    feedItems.value = await familyApi.getFeed()
  } catch (error) {
    console.error('Failed to load feed:', error)
  } finally {
    loadingFeed.value = false
  }
}

const loadComments = async (excerptId: number) => {
  loadingComments[excerptId] = true
  try {
    commentsMap[excerptId] = await excerptApi.getComments(excerptId)
  } catch (error) {
    console.error('Failed to load comments:', error)
    commentsMap[excerptId] = []
  } finally {
    loadingComments[excerptId] = false
  }
}

const openCommentDialog = (excerpt: ProgramExcerpt) => {
  currentExcerpt.value = excerpt
  commentContent.value = ''
  commentDialogVisible.value = true
  loadComments(excerpt.id)
}

const handleSubmitComment = async () => {
  if (!currentExcerpt.value || !commentContent.value.trim()) return

  submittingComment.value = true
  try {
    await excerptApi.addComment(currentExcerpt.value.id, commentContent.value.trim())
    ElMessage.success('评论发表成功！')
    commentDialogVisible.value = false
    loadComments(currentExcerpt.value.id)
  } catch (error) {
    console.error('Submit comment error:', error)
  } finally {
    submittingComment.value = false
  }
}

onMounted(async () => {
  await loadMembers()
  await loadFeed()
})
</script>
