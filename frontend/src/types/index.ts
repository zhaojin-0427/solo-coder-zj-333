export interface ProgramExcerpt {
  id: number
  date: string
  programName: string
  timeSlot: string
  contentSummary: string
  elderlyNotes: string
  topicId: number | null
  isDuplicate: boolean
  duplicateOf: number | null
  createdBy: number
  createdAt: string
  updatedAt: string
  versions?: Version[]
  topic?: Topic
}

export interface Topic {
  id: number
  name: string
  color: string
  icon: string
  description: string
  count?: number
}

export interface Version {
  id: number
  excerptId: number
  content: string
  createdBy: number
  createdAt: string
  mergeNote: string
}

export interface FamilyMember {
  id: number
  name: string
  role: 'elderly' | 'family' | 'admin'
  avatar: string
  contributionCount: number
  username?: string
}

export interface FollowUpItem {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'high' | 'medium' | 'low'
  excerptId: number
  assignedTo: number
  dueDate: string
  createdAt: string
  excerpt?: ProgramExcerpt
}

export interface Comment {
  id: number
  excerptId: number
  userId: number
  content: string
  createdAt: string
  user?: FamilyMember
}

export interface Statistics {
  topPrograms: { name: string; count: number }[]
  topicDistribution: { name: string; count: number; color: string }[]
  duplicateRate: { total: number; duplicates: number; rate: number }
  confirmationStatus: { pending: number; confirmed: number; rejected: number }
}

export interface User {
  id: number
  username: string
  name: string
  role: string
  avatar: string
  familyGroupId?: number
  token?: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface ApiResponse<T> {
  data: T
  status?: number
  message?: string
}

export interface PaginationParams {
  page?: number
  pageSize?: number
}

export interface ExcerptFilterParams extends PaginationParams {
  topicId?: number
  date?: string
  includeDuplicates?: boolean
}
