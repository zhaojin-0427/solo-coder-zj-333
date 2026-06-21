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
            <el-loading text="加载中..." />
          </div>
          <div v-else-if="members.length === 0" class="py-8">
            <el-empty description="暂无家庭成员" />
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="member in members"
              :key="member.id"
              class="flex items-center gap-4 p-4 bg-orange-50 rounded-xl"
            >
              <div class="member-avatar text-3xl">
                {{ member.avatar }}
              </div>
              <div class="flex-1">
                <p class="text-lg font-semibold">{{ member.name }}</p>
                <p class="text-sm text-gray-500">
                  {{ member.role === 'elderly' ? '长辈' : member.role === 'admin' ? '管理员' : '家人' }}
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
            <el-loading text="加载中..." size="large" />
          </div>

          <div v-else-if="feedItems.length === 0" class="py-8">
            <el-empty description="暂无动态，快去记录第一条节目吧！" />
          </div>

          <div v-else class="timeline">
            <div
              v-for="item in feedItems"
              :key="item.data.id"
              class="timeline-item"
            >
              <el-card class="shadow-card-hover" :body-style="{ padding: '20px' }">
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <span class="text-3xl">📻</span>
                      <div>
                        <h3 class="text-xl font-semibold">{{ item.data.programName }}</h3>
                        <p class="text-sm text-gray-500">
                          📅 {{ item.data.date }} · ⏰ {{ item.data.timeSlot }}
                        </p>
                      </div>
                    </div>
                    <el-tag
                      v-if="item.data.topic"
                      :style="{ backgroundColor: item.data.topic.color + '20', color: item.data.topic.color }"
                      size="large"
                    >
                      {{ item.data.topic.icon }} {{ item.data.topic.name }}
                    </el-tag>
                  </div>

                  <div class="text-base text-gray-700">
                    <span class="font-medium">内容摘要：</span>
                    {{ item.data.contentSummary }}
                  </div>

                  <div
                    v-if="item.data.elderlyNotes"
                    class="bg-elderly rounded-lg p-4"
                  >
                    <div class="flex items-center gap-2 mb-2">
                      <span class="text-xl">👴</span>
                      <span class="font-semibold text-primary">老人补充</span>
                    </div>
                    <p class="text-lg text-gray-800">{{ item.data.elderlyNotes }}</p>
                  </div>

                  <el-divider class="my-3" />

                  <div>
                    <div class="flex items-center justify-between mb-3">
                      <h4 class="text-lg font-semibold">💬 评论 ({{ commentsMap[item.data.id]?.length || 0 }})</h4>
                      <el-button
                        type="primary"
                        size="large"
                        @click="openCommentDialog(item.data)"
                      >
                        ✏️ 发表评论
                      </el-button>
                    </div>

                    <div v-if="loadingComments[item.data.id]" class="py-4 text-center text-gray-500">
                      加载评论中...
                    </div>

                    <div v-else-if="commentsMap[item.data.id]?.length > 0" class="space-y-3">
                      <div
                        v-for="comment in commentsMap[item.data.id]"
                        :key="comment.id"
                        class="flex gap-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <div class="text-2xl">
                          {{ getUserAvatar(comment.userId) }}
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center gap-2 mb-1">
                            <span class="font-medium">{{ getUserName(comment.userId) }}</span>
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
          <p class="font-semibold text-lg">{{ currentExcerpt.programName }}</p>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FamilyMember, ProgramExcerpt, Comment } from '@/types'
import { familyApi, excerptApi } from '@/api'

const loadingMembers = ref(false)
const loadingFeed = ref(false)
const submittingComment = ref(false)

const members = ref<FamilyMember[]>([])
const feedItems = ref<{ type: string; data: ProgramExcerpt }[]>([])

const commentsMap = reactive<Record<number, Comment[]>>({})
const loadingComments = reactive<Record<number, boolean>>({})

const currentExcerpt = ref<ProgramExcerpt | null>(null)
const commentDialogVisible = ref(false)
const commentContent = ref('')

const userMap = reactive<Record<number, FamilyMember>>({})

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

const getUserAvatar = (userId: number) => {
  return userMap[userId]?.avatar || '👤'
}

const getUserName = (userId: number) => {
  return userMap[userId]?.name || '未知用户'
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

onMounted(() => {
  loadMembers()
  loadFeed()
})
</script>
