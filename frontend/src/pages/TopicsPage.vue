<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📁</span>
      <span>专题整理</span>
    </h1>

    <div class="form-section mb-6">
      <div class="flex flex-wrap gap-3">
        <div
          class="px-6 py-3 rounded-full cursor-pointer transition-all duration-200 text-lg font-medium"
          :class="activeTopicId === -1 ? 'bg-gray-800 text-white shadow-lg' : 'bg-white text-gray-700 hover:shadow-md border-2 border-gray-200'"
          @click="selectTopic(-1)"
        >
          <span class="mr-2">📋</span>
          <span>全部</span>
          <el-tag
            size="large"
            class="ml-2"
            :style="{ backgroundColor: activeTopicId === -1 ? 'rgba(255,255,255,0.3)' : '#33333320', color: activeTopicId === -1 ? 'white' : '#333' }"
          >
            {{ allExcerpts.length }}
          </el-tag>
        </div>
        <div
          v-for="topic in topics"
          :key="topic.id"
          class="px-6 py-3 rounded-full cursor-pointer transition-all duration-200 text-lg font-medium"
          :class="activeTopicId === topic.id ? 'text-white shadow-lg' : 'bg-white text-gray-700 hover:shadow-md'"
          :style="activeTopicId === topic.id ? { backgroundColor: topic.color } : { border: `2px solid ${topic.color}30` }"
          @click="selectTopic(topic.id)"
        >
          <span class="mr-2">{{ topic.icon }}</span>
          <span>{{ topic.name }}</span>
          <el-tag
            size="large"
            class="ml-2"
            :style="{ backgroundColor: activeTopicId === topic.id ? 'rgba(255,255,255,0.3)' : topic.color + '20', color: activeTopicId === topic.id ? 'white' : topic.color }"
          >
            {{ topic.excerptCount || 0 }}
          </el-tag>
        </div>
        <div
          class="px-6 py-3 rounded-full cursor-pointer transition-all duration-200 text-lg font-medium"
          :class="activeTopicId === null ? 'bg-orange-400 text-white shadow-lg' : 'bg-white text-gray-700 hover:shadow-md border-2 border-orange-200'"
          @click="selectTopic(null)"
        >
          <span class="mr-2">🗂️</span>
          <span>未归类</span>
          <el-tag
            size="large"
            class="ml-2"
            :style="{ backgroundColor: activeTopicId === null ? 'rgba(255,255,255,0.3)' : '#FF7A4520', color: activeTopicId === null ? 'white' : '#FF7A45' }"
          >
            {{ uncategorizedCount }}
          </el-tag>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="text-gray-500 text-lg">⏳ 加载中...</div>
    </div>

    <div v-else-if="excerpts.length === 0" class="loading-container">
      <el-empty description="该分类下暂无内容" />
    </div>

    <div v-else class="card-grid">
      <el-card
        v-for="excerpt in excerpts"
        :key="excerpt.id"
        class="shadow-card-hover cursor-pointer"
        :body-style="{ padding: '20px' }"
        @click="openDetail(excerpt)"
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
                ⚠️ 重复
              </span>
            </div>
            <el-tag
              v-if="excerpt.topic"
              :style="{ backgroundColor: excerpt.topic.color + '20', color: excerpt.topic.color, borderColor: excerpt.topic.color }"
              effect="light"
            >
              {{ excerpt.topic.icon }} {{ excerpt.topic.name }}
            </el-tag>
            <el-tag v-else type="warning" effect="light">
              🗂️ 未归类
            </el-tag>
          </div>
        </template>

        <div class="space-y-3">
          <div class="flex items-center gap-4 text-base text-gray-600">
            <span>📅 {{ excerpt.date }}</span>
            <span>⏰ {{ excerpt.timeSlot }}</span>
            <span>👤 {{ excerpt.createdByName }}</span>
            <span>💬 {{ excerpt.commentCount }} 条评论</span>
          </div>

          <div class="text-base text-gray-700 line-clamp-3">
            {{ excerpt.contentSummary }}
          </div>

          <div
            v-if="excerpt.elderlyNotes"
            class="bg-elderly rounded-lg p-3 mt-3"
          >
            <div class="flex items-center gap-2 mb-1">
              <span>👴</span>
              <span class="font-semibold text-primary text-sm">老人补充</span>
            </div>
            <p class="text-base text-gray-800 line-clamp-2">{{ excerpt.elderlyNotes }}</p>
          </div>

          <el-divider class="my-3" />

          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-500">
              创建于 {{ formatTime(excerpt.createdAt) }}
            </div>
            <div class="flex gap-2">
              <el-button
                size="large"
                type="primary"
                @click.stop="openCategorizeDialog(excerpt)"
              >
                🏷️ 归类
              </el-button>
              <el-button
                size="large"
                @click.stop="openVersionsDialog(excerpt)"
              >
                📜 历史版本
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="detailDialogVisible"
      title="📖 内容详情"
      width="600px"
      size="large"
    >
      <div v-if="currentExcerpt" class="space-y-4">
        <div class="flex items-center gap-2">
          <span class="text-3xl">📻</span>
          <h3 class="text-2xl font-bold">{{ currentExcerpt.programName }}</h3>
          <span
            v-if="currentExcerpt.isDuplicate"
            class="duplicate-badge"
          >
            ⚠️ 重复记录
          </span>
        </div>

        <div class="flex items-center gap-4 text-lg text-gray-600">
          <span>📅 {{ currentExcerpt.date }}</span>
          <span>⏰ {{ currentExcerpt.timeSlot }}</span>
        </div>

        <div class="flex items-center gap-2">
          <el-tag
            v-if="currentExcerpt.topic"
            size="large"
            :style="{ backgroundColor: currentExcerpt.topic.color + '20', color: currentExcerpt.topic.color }"
          >
            {{ currentExcerpt.topic.icon }} {{ currentExcerpt.topic.name }}
          </el-tag>
          <el-tag v-else type="warning" size="large">
            🗂️ 未归类
          </el-tag>
          <el-tag size="large" type="info">
            👤 {{ currentExcerpt.createdByName }}
          </el-tag>
          <el-tag size="large" type="success">
            💬 {{ currentExcerpt.commentCount }} 条评论
          </el-tag>
        </div>

        <el-divider />

        <div>
          <h4 class="text-lg font-semibold mb-2">📝 内容摘要</h4>
          <p class="text-base text-gray-700 leading-relaxed whitespace-pre-wrap">{{ currentExcerpt.contentSummary }}</p>
        </div>

        <div
          v-if="currentExcerpt.elderlyNotes"
          class="bg-elderly rounded-lg p-4"
        >
          <h4 class="text-lg font-semibold mb-2 text-primary">👴 老人补充</h4>
          <p class="text-lg text-gray-800 leading-relaxed whitespace-pre-wrap">{{ currentExcerpt.elderlyNotes }}</p>
        </div>
      </div>

      <template #footer>
        <el-button size="large" @click="detailDialogVisible = false">
          关闭
        </el-button>
        <el-button type="primary" size="large" @click="openCategorizeDialog(currentExcerpt!)">
          🏷️ 修改归类
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="categorizeDialogVisible"
      title="🏷️ 选择专题分类"
      width="500px"
      size="large"
    >
      <div class="space-y-4">
        <p class="text-lg text-gray-700">
          为《{{ currentExcerpt?.programName }}》选择专题分类：
        </p>
        <div class="space-y-3">
          <div
            v-for="topic in topics"
            :key="topic.id"
            class="flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all duration-200 border-2"
            :class="selectedTopicId === topic.id ? 'border-primary bg-primary-light' : 'border-gray-100 hover:border-gray-200 bg-white'"
            @click="selectedTopicId = topic.id"
          >
            <span class="text-3xl">{{ topic.icon }}</span>
            <div class="flex-1">
              <p class="text-lg font-semibold" :style="{ color: topic.color }">{{ topic.name }}</p>
              <p class="text-sm text-gray-500">{{ topic.description }}</p>
            </div>
            <el-tag size="large" :style="{ backgroundColor: topic.color + '20', color: topic.color }">
              {{ topic.excerptCount }} 条
            </el-tag>
          </div>
          <div
            class="flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all duration-200 border-2"
            :class="selectedTopicId === null ? 'border-primary bg-primary-light' : 'border-gray-100 hover:border-gray-200 bg-white'"
            @click="selectedTopicId = null"
          >
            <span class="text-3xl">🗂️</span>
            <div class="flex-1">
              <p class="text-lg font-semibold text-gray-700">取消归类</p>
              <p class="text-sm text-gray-500">不分配到任何专题</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button size="large" @click="categorizeDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          size="large"
          :loading="categorizing"
          @click="handleCategorize"
        >
          确认归类
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="versionsDialogVisible"
      title="📜 历史版本"
      width="600px"
      size="large"
    >
      <div v-if="loadingVersions" class="loading-container py-8">
        <div class="text-gray-500 text-lg">⏳ 加载中...</div>
      </div>
      <div v-else-if="versions.length === 0" class="py-8">
        <el-empty description="暂无版本历史" />
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="(version, index) in versions"
          :key="version.id"
          class="p-4 bg-orange-50 rounded-xl border-l-4 border-primary"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-lg">
              版本 {{ versions.length - index }}
            </span>
            <span class="text-sm text-gray-500">
              {{ formatTime(version.createdAt) }}
            </span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xl">{{ version.createdBy?.avatar || '👤' }}</span>
            <span class="text-sm text-gray-600">{{ version.createdBy?.firstName || '未知用户' }}</span>
          </div>
          <p class="text-base text-gray-700 mb-2 whitespace-pre-wrap">{{ version.content }}</p>
          <p v-if="version.mergeNote" class="text-sm text-gray-500 bg-white p-2 rounded">
            📝 合并备注：{{ version.mergeNote }}
          </p>
        </div>
      </div>

      <template #footer>
        <el-button size="large" @click="versionsDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { ProgramExcerpt, Topic, Version } from '@/types'
import { excerptApi, topicApi } from '@/api'

const loading = ref(false)
const categorizing = ref(false)
const loadingVersions = ref(false)

const activeTopicId = ref<number | null | -1>(-1)
const selectedTopicId = ref<number | null>(null)

const topics = ref<Topic[]>([])
const excerpts = ref<ProgramExcerpt[]>([])
const allExcerpts = ref<ProgramExcerpt[]>([])
const versions = ref<Version[]>([])

const currentExcerpt = ref<ProgramExcerpt | null>(null)

const detailDialogVisible = ref(false)
const categorizeDialogVisible = ref(false)
const versionsDialogVisible = ref(false)

const uncategorizedCount = computed(() => {
  return allExcerpts.value.filter(e => !e.topic).length
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
    allExcerpts.value = await excerptApi.getList()
    filterExcerpts()
  } catch (error) {
    console.error('Failed to load excerpts:', error)
  } finally {
    loading.value = false
  }
}

const filterExcerpts = () => {
  if (activeTopicId.value === -1) {
    excerpts.value = allExcerpts.value
  } else if (activeTopicId.value === null) {
    excerpts.value = allExcerpts.value.filter(e => !e.topic)
  } else {
    excerpts.value = allExcerpts.value.filter(e => e.topic?.id === activeTopicId.value)
  }
}

const selectTopic = (topicId: number | null | -1) => {
  activeTopicId.value = topicId
  filterExcerpts()
}

const openDetail = (excerpt: ProgramExcerpt) => {
  currentExcerpt.value = excerpt
  detailDialogVisible.value = true
}

const openCategorizeDialog = (excerpt: ProgramExcerpt) => {
  currentExcerpt.value = excerpt
  selectedTopicId.value = excerpt.topic ? excerpt.topic.id : null
  categorizeDialogVisible.value = true
  detailDialogVisible.value = false
}

const handleCategorize = async () => {
  if (!currentExcerpt.value) return

  categorizing.value = true
  try {
    await excerptApi.update(currentExcerpt.value.id, {
      topicId: selectedTopicId.value
    })
    ElMessage.success('归类成功！')
    categorizeDialogVisible.value = false
    loadTopics()
    loadExcerpts()
  } catch (error) {
    console.error('Categorize error:', error)
  } finally {
    categorizing.value = false
  }
}

const openVersionsDialog = async (excerpt: ProgramExcerpt) => {
  currentExcerpt.value = excerpt
  versionsDialogVisible.value = true
  loadingVersions.value = true
  try {
    versions.value = await excerptApi.getVersions(excerpt.id)
  } catch (error) {
    console.error('Failed to load versions:', error)
  } finally {
    loadingVersions.value = false
  }
}

onMounted(() => {
  loadTopics()
  loadExcerpts()
})
</script>
