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
  ExcerptFilterParams
} from '@/types'

const baseURL = 'http://localhost:9422/api'

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
    api.post(`/excerpts/${id}/comments/`, { content })
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

  getFeed: (): Promise<{ type: string; data: ProgramExcerpt }[]> =>
    api.get('/family/feed/')
}

export const followUpApi = {
  getList: (status?: string): Promise<FollowUpItem[]> => {
    const query = status ? `?status=${status}` : ''
    return api.get(`/followups/${query}`)
  },

  create: (data: Partial<FollowUpItem> & { assignedToId?: number | null }): Promise<FollowUpItem> =>
    api.post('/followups/', {
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority,
      excerptId: data.excerptId,
      assignedToId: data.assignedToId ?? (typeof data.assignedTo === 'object' ? data.assignedTo?.id : data.assignedTo),
      dueDate: data.dueDate
    }),

  update: (id: number, data: Partial<FollowUpItem> & { assignedToId?: number | null }): Promise<FollowUpItem> =>
    api.put(`/followups/${id}/`, {
      title: data.title,
      description: data.description,
      status: data.status,
      priority: data.priority,
      excerptId: data.excerptId,
      assignedToId: data.assignedToId ?? (typeof data.assignedTo === 'object' ? data.assignedTo?.id : data.assignedTo),
      dueDate: data.dueDate
    }),

  updateStatus: (id: number, status: string): Promise<FollowUpItem> =>
    api.put(`/followups/${id}/`, { status })
}

export const statisticsApi = {
  getStatistics: (): Promise<Statistics> =>
    api.get('/statistics/')
}

export default api
