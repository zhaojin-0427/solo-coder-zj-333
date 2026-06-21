import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { convertKeysSnakeToCamel, convertKeysCamelToSnake } from '@/utils/convert'
import type {
  ProgramExcerpt,
  Topic,
  Version,
  FamilyMember,
  FollowUpItem,
  Comment,
  Statistics,
  LoginResponse,
  ExcerptFilterParams,
  ConfirmationInfo,
  ReviewPackage,
  ReviewPackageItem,
  ReviewPackageFeedback,
  FeedItem,
  CompanionPlan,
  CompanionPlanMaterial
} from '@/types'

const baseURL = 'http://localhost:8000/api'

const axiosInstance: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (config.data && typeof config.data === 'object' && !(config.data instanceof FormData)) {
      config.data = convertKeysCamelToSnake(config.data)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    response.data = convertKeysSnakeToCamel(response.data)
    return response
  },
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        ElMessage.error('登录已过期，请重新登录')
        window.location.href = '/login'
      } else if (status === 403) {
        ElMessage.error('没有权限访问')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      } else if (error.response.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error(error.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

const api = {
  get: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.get(url, config).then((res) => res.data),

  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.post(url, data, config).then((res) => res.data),

  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.put(url, data, config).then((res) => res.data),

  delete: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.delete(url, config).then((res) => res.data)
}

export const authApi = {
  login: (username: string, password: string): Promise<LoginResponse> =>
    api.post('/auth/login/', { username, password })
}

export const excerptApi = {
  getList: (params?: ExcerptFilterParams): Promise<ProgramExcerpt[]> => {
    const queryParams = new URLSearchParams()
    if (params?.topicId) queryParams.append('topic_id', params.topicId.toString())
    if (params?.date) queryParams.append('date', params.date)
    if (params?.includeDuplicates !== undefined) {
      queryParams.append('include_duplicates', params.includeDuplicates.toString())
    }
    if (params?.confirmationStatus) {
      queryParams.append('confirmation_status', params.confirmationStatus)
    }
    return api.get(`/excerpts/${queryParams.toString() ? '?' + queryParams.toString() : ''}`)
  },

  getDetail: (id: number): Promise<ProgramExcerpt> =>
    api.get(`/excerpts/${id}/`),

  create: (data: Partial<ProgramExcerpt>): Promise<ProgramExcerpt> =>
    api.post('/excerpts/', {
      date: data.date,
      programName: data.programName,
      timeSlot: data.timeSlot,
      contentSummary: data.contentSummary,
      elderlyNotes: data.elderlyNotes,
      topicId: data.topicId
    }),

  update: (id: number, data: Partial<ProgramExcerpt>): Promise<ProgramExcerpt> =>
    api.put(`/excerpts/${id}/`, {
      date: data.date,
      programName: data.programName,
      timeSlot: data.timeSlot,
      contentSummary: data.contentSummary,
      elderlyNotes: data.elderlyNotes,
      topicId: data.topicId
    }),

  delete: (id: number): Promise<void> =>
    api.delete(`/excerpts/${id}/`),

  getVersions: (id: number): Promise<Version[]> =>
    api.get(`/excerpts/${id}/versions/`),

  mergeDuplicate: (id: number, duplicateId: number, mergeNote?: string): Promise<ProgramExcerpt> =>
    api.post(`/excerpts/${id}/merge/`, {
      duplicateId: duplicateId,
      mergeNote: mergeNote
    }),

  getComments: (id: number): Promise<Comment[]> =>
    api.get(`/excerpts/${id}/comments/`),

  addComment: (id: number, content: string): Promise<Comment> =>
    api.post(`/excerpts/${id}/comments/`, { content }),

  confirm: (id: number, confirmationStatus: 'confirmed' | 'needs_verification', confirmationNote: string = '', generateFollowup: boolean = false): Promise<ProgramExcerpt> =>
    api.post(`/excerpts/${id}/confirm/`, {
      confirmationStatus,
      confirmationNote,
      generateFollowup
    })
}

export const topicApi = {
  getList: (): Promise<Topic[]> =>
    api.get('/topics/'),

  create: (data: Partial<Topic>): Promise<Topic> =>
    api.post('/topics/', {
      name: data.name,
      color: data.color,
      icon: data.icon,
      description: data.description
    }),

  update: (id: number, data: Partial<Topic>): Promise<Topic> =>
    api.put(`/topics/${id}/`, {
      name: data.name,
      color: data.color,
      icon: data.icon,
      description: data.description
    })
}

export const familyApi = {
  getMembers: (): Promise<FamilyMember[]> =>
    api.get('/family/members/'),

  getFeed: (): Promise<FeedItem[]> =>
    api.get('/family/feed/')
}

export const followUpApi = {
  getList: (status?: string): Promise<FollowUpItem[]> => {
    const query = status ? `?status=${status}` : ''
    return api.get(`/followups/${query}`)
  },

  create: (data: Partial<FollowUpItem> & { assignedToId?: number | null; reviewPackageItemId?: number | null; companionPlanId?: number | null }): Promise<FollowUpItem> =>
    api.post('/followups/', {
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority,
      excerptId: data.excerptId,
      reviewPackageItemId: data.reviewPackageItemId,
      companionPlanId: data.companionPlanId,
      assignedToId: data.assignedToId ?? (typeof data.assignedTo === 'object' ? data.assignedTo?.id : data.assignedTo),
      dueDate: data.dueDate
    }),

  update: (id: number, data: Partial<FollowUpItem> & { assignedToId?: number | null; reviewPackageItemId?: number | null; companionPlanId?: number | null }): Promise<FollowUpItem> =>
    api.put(`/followups/${id}/`, {
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority,
      excerptId: data.excerptId,
      reviewPackageItemId: data.reviewPackageItemId,
      companionPlanId: data.companionPlanId,
      assignedToId: data.assignedToId ?? (typeof data.assignedTo === 'object' ? data.assignedTo?.id : data.assignedTo),
      dueDate: data.dueDate
    }),

  updateStatus: (id: number, status: string): Promise<FollowUpItem> =>
    api.put(`/followups/${id}/`, { status })
}

export const companionPlanApi = {
  getList: (status?: string): Promise<CompanionPlan[]> => {
    const query = status ? `?status=${status}` : ''
    return api.get(`/companion-plans/${query}`)
  },

  getDetail: (id: number): Promise<CompanionPlan> =>
    api.get(`/companion-plans/${id}/`),

  create: (data: {
    title: string
    handleLocation: string
    sourceType?: 'excerpt' | 'topic' | 'manual'
    sourceExcerptId?: number | null
    sourceTopicId?: number | null
    sourceExcerptContent?: string | null
    handleTimeStart?: string | null
    handleTimeEnd?: string | null
    handleTimeNote?: string | null
    transportation?: 'walk' | 'bus' | 'subway' | 'taxi' | 'private_car' | 'community_shuttle' | 'other' | null
    transportationNote?: string | null
    companionUserId?: number | null
    elderlyNotes?: string | null
    materials?: { name: string; description?: string | null; orderIndex?: number }[]
    status?: 'pending' | 'preparing' | 'scheduled' | 'completed' | 'cancelled'
  }): Promise<CompanionPlan> =>
    api.post('/companion-plans/', {
      title: data.title,
      handleLocation: data.handleLocation,
      sourceType: data.sourceType,
      sourceExcerptId: data.sourceExcerptId,
      sourceTopicId: data.sourceTopicId,
      sourceExcerptContent: data.sourceExcerptContent,
      handleTimeStart: data.handleTimeStart,
      handleTimeEnd: data.handleTimeEnd,
      handleTimeNote: data.handleTimeNote,
      transportation: data.transportation,
      transportationNote: data.transportationNote,
      companionUserId: data.companionUserId,
      elderlyNotes: data.elderlyNotes,
      materials: data.materials,
      status: data.status
    }),

  update: (id: number, data: {
    title?: string
    handleLocation?: string
    sourceType?: 'excerpt' | 'topic' | 'manual'
    sourceExcerptId?: number | null
    sourceTopicId?: number | null
    sourceExcerptContent?: string | null
    handleTimeStart?: string | null
    handleTimeEnd?: string | null
    handleTimeNote?: string | null
    transportation?: 'walk' | 'bus' | 'subway' | 'taxi' | 'private_car' | 'community_shuttle' | 'other' | null
    transportationNote?: string | null
    companionUserId?: number | null
    elderlyNotes?: string | null
    elderlyConcerns?: string | null
    status?: 'pending' | 'preparing' | 'scheduled' | 'completed' | 'cancelled'
    materialsConfirmed?: boolean
    timeLocationKnown?: boolean
    needsCompanion?: boolean
    materials?: { name: string; description?: string | null; orderIndex?: number }[]
  }): Promise<CompanionPlan> =>
    api.put(`/companion-plans/${id}/`, data),

  remove: (id: number): Promise<void> =>
    api.delete(`/companion-plans/${id}/`),

  elderlyCheckin: (id: number, data: {
    materialsConfirmed?: boolean
    timeLocationKnown?: boolean
    needsCompanion?: boolean
    elderlyConcerns?: string | null
    materialIds?: number[]
  }): Promise<CompanionPlan> =>
    api.post(`/companion-plans/${id}/elderly-checkin/`, data),

  getMaterials: (planId?: number): Promise<CompanionPlanMaterial[]> => {
    const query = planId ? `?plan_id=${planId}` : ''
    return api.get(`/companion-plan-materials/${query}`)
  },

  updateMaterialStatus: (materialId: number, isPrepared: boolean): Promise<CompanionPlanMaterial> =>
    api.post(`/companion-plan-materials/${materialId}/update-status/`, {
      isPrepared
    })
}

export const reviewPackageApi = {
  getList: (): Promise<ReviewPackage[]> =>
    api.get('/review-packages/'),

  getDetail: (id: number): Promise<ReviewPackage> =>
    api.get(`/review-packages/${id}/`),

  create: (data: {
    title: string
    purposeDescription?: string | null
    guideText?: string | null
    excerptIds: number[]
    itemsConfig?: Record<string, { isHighlighted?: boolean; familyReminder?: string }>
  }): Promise<ReviewPackage> =>
    api.post('/review-packages/', {
      title: data.title,
      purposeDescription: data.purposeDescription,
      guideText: data.guideText,
      excerptIds: data.excerptIds,
      itemsConfig: data.itemsConfig
    }),

  update: (id: number, data: {
    title?: string
    purposeDescription?: string | null
    guideText?: string | null
    excerptIds?: number[]
    itemsConfig?: Record<string, { isHighlighted?: boolean; familyReminder?: string }>
  }): Promise<ReviewPackage> =>
    api.put(`/review-packages/${id}/`, {
      title: data.title,
      purposeDescription: data.purposeDescription,
      guideText: data.guideText,
      excerptIds: data.excerptIds,
      itemsConfig: data.itemsConfig
    }),

  remove: (id: number): Promise<void> =>
    api.delete(`/review-packages/${id}/`),

  reorderItems: (packageId: number, orderedItemIds: number[]): Promise<ReviewPackageItem[]> =>
    api.post(`/review-packages/${packageId}/reorder-items/`, {
      orderedItemIds
    }),

  getFeedbacks: (packageId: number): Promise<ReviewPackageFeedback[]> =>
    api.get(`/review-packages/${packageId}/feedbacks/`),

  getItemList: (packageId?: number): Promise<ReviewPackageItem[]> => {
    const query = packageId ? `?package_id=${packageId}` : ''
    return api.get(`/review-package-items/${query}`)
  },

  updateItemConfig: (itemId: number, data: { isHighlighted?: boolean; familyReminder?: string | null }): Promise<ReviewPackageItem> =>
    api.post(`/review-package-items/${itemId}/update-config/`, {
      isHighlighted: data.isHighlighted,
      familyReminder: data.familyReminder
    }),

  submitFeedback: (itemId: number, feedbackType: 'read' | 'review_again' | 'needs_explanation', note?: string): Promise<ReviewPackageFeedback> =>
    api.post(`/review-package-items/${itemId}/submit-feedback/`, {
      feedbackType,
      note
    })
}

export const statisticsApi = {
  getStatistics: (): Promise<Statistics> =>
    api.get('/statistics/')
}

export default api
