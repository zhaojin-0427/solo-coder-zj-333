export interface FamilyGroup {
  id: number
  name: string
  createdAt: string
}

export interface UserInfo {
  id: number
  username: string
  firstName: string
  lastName: string
  email: string
  role: 'elderly' | 'family' | 'admin'
  roleDisplay: string
  avatar: string
  familyGroup: FamilyGroup | null
  isActive: boolean
  isStaff: boolean
  dateJoined: string
}

export interface ProgramExcerpt {
  id: number
  date: string
  programName: string
  timeSlot: string
  contentSummary: string
  elderlyNotes: string
  topic: Topic | null
  topicId?: number | null
  topicName: string | null
  isDuplicate: boolean
  duplicateOf: number | null
  createdBy: UserInfo
  createdByName: string
  confirmationStatus: 'pending' | 'confirmed' | 'needs_verification'
  confirmationStatusDisplay: string
  confirmedByName: string | null
  confirmedAt: string | null
  confirmationNote: string | null
  commentCount: number
  versions?: Version[]
  comments?: Comment[]
  createdAt: string
  updatedAt: string
}

export interface Topic {
  id: number
  name: string
  color: string
  icon: string
  description: string
  excerptCount: number
  createdAt: string
}

export interface Version {
  id: number
  content: string
  createdBy: UserInfo
  createdAt: string
  mergeNote: string
}

export interface FamilyMember {
  id: number
  username: string
  firstName: string
  lastName: string
  email: string
  role: 'elderly' | 'family' | 'admin'
  roleDisplay: string
  avatar: string
  familyGroup: FamilyGroup | null
  isActive: boolean
  isStaff: boolean
  dateJoined: string
  contributionCount?: number
}

export interface FollowUpItem {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  statusDisplay: string
  priority: 'high' | 'medium' | 'low'
  priorityDisplay: string
  sourceType: 'manual' | 'confirmation'
  sourceTypeDisplay: string
  excerpt: ProgramExcerpt | null
  excerptId?: number | null
  assignedTo: UserInfo | null
  assignedToId?: number | null
  assignedToName: string | null
  dueDate: string
  createdAt: string
}

export interface Comment {
  id: number
  user: UserInfo
  content: string
  createdAt: string
}

export interface Statistics {
  popularPrograms: { name: string; count: number }[]
  topicDistribution: { name: string; count: number; color: string }[]
  duplicateRatio: { total: number; duplicates: number; rate: number }
  unconfirmedExcerpts: number
  pendingFollowups: number
  totalExcerpts: number
  confirmationStatus: { pending: number; confirmed: number; needsVerification: number }
  pendingConfirmationCount: number
  confirmationTrend7d: { date: string; count: number }[]
}

export interface User {
  id: number
  username: string
  firstName: string
  lastName: string
  email: string
  role: string
  roleDisplay: string
  avatar: string
  familyGroup: FamilyGroup | null
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
  confirmationStatus?: string
}

export interface ConfirmationInfo {
  confirmedByName: string
  confirmedAt: string
  confirmationNote: string
  confirmationStatus: string
  confirmationStatusDisplay: string
}
