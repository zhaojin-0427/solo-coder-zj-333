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

export interface ReviewPackageItem {
  id: number
  excerpt: ProgramExcerpt | null
  excerptId?: number
  orderIndex: number
  isHighlighted: boolean
  familyReminder: string | null
  feedbackType: 'read' | 'review_again' | 'needs_explanation' | null
  feedbackCount: number
  latestFeedback: ReviewPackageFeedbackInfo | null
  createdAt: string
}

export interface ReviewPackageFeedbackInfo {
  id: number
  feedbackType: 'read' | 'review_again' | 'needs_explanation'
  feedbackTypeDisplay: string
  note: string | null
  elderlyUserName: string
  createdAt: string
}

export interface ReviewPackage {
  id: number
  title: string
  purposeDescription: string | null
  guideText: string | null
  createdBy: UserInfo | null
  createdByName: string
  itemCount: number
  feedbackCount: number
  items?: ReviewPackageItem[]
  createdAt: string
  updatedAt: string
}

export interface ReviewPackageFeedback {
  id: number
  packageItem: ReviewPackageItem | null
  elderlyUser: UserInfo | null
  elderlyUserName: string
  feedbackType: 'read' | 'review_again' | 'needs_explanation'
  feedbackTypeDisplay: string
  note: string | null
  createdAt: string
  generatedFollowup?: FollowUpItem | null
}

export interface ReviewPackageFeedItem {
  id: number
  feedbackType: 'read' | 'review_again' | 'needs_explanation'
  feedbackTypeDisplay: string
  note: string | null
  elderlyUserName: string
  elderlyUserAvatar: string
  packageId: number
  packageTitle: string
  packageItemId: number
  excerptProgramName: string
  excerptContentSummary: string
}

export interface ReviewPackageStats {
  totalPackages: number
  totalItems: number
  highlightedItems: number
  feedbackDistribution: {
    read: number
    reviewAgain: number
    needsExplanation: number
  }
  topicDistribution: {
    id: number
    name: string
    color: string
    icon: string
    count: number
  }[]
  needsExplanationCount: number
}

export interface CompanionPlanMaterial {
  id: number
  name: string
  description: string | null
  isPrepared: boolean
  preparedBy: UserInfo | null
  preparedByName: string | null
  preparedAt: string | null
  orderIndex: number
  createdAt: string
}

export interface CompanionPlan {
  id: number
  title: string
  sourceType: 'excerpt' | 'topic' | 'manual'
  sourceTypeDisplay: string
  sourceExcerpt: ProgramExcerpt | null
  sourceExcerptId?: number | null
  sourceTopic: Topic | null
  sourceTopicId?: number | null
  sourceExcerptContent: string | null
  handleLocation: string
  handleTimeStart: string | null
  handleTimeEnd: string | null
  handleTimeNote: string | null
  transportation: 'walk' | 'bus' | 'subway' | 'taxi' | 'private_car' | 'community_shuttle' | 'other' | null
  transportationDisplay: string | null
  transportationNote: string | null
  companionUser: UserInfo | null
  companionUserId?: number | null
  companionUserName: string | null
  elderlyNotes: string | null
  elderlyConcerns: string | null
  status: 'pending' | 'preparing' | 'scheduled' | 'completed' | 'cancelled'
  statusDisplay: string
  materialsConfirmed: boolean
  timeLocationKnown: boolean
  needsCompanion: boolean
  createdBy: UserInfo | null
  createdByName: string
  materials?: CompanionPlanMaterial[]
  materialCount: number
  preparedMaterialCount: number
  materialPreparedRate: number
  createdAt: string
  updatedAt: string
}

export interface CompanionPlanStats {
  totalPlans: number
  statusDistribution: {
    pending: number
    preparing: number
    scheduled: number
    completed: number
    cancelled: number
  }
  materialPreparedRate: number
  pending7d: number
  topLocations: { location: string; count: number }[]
}

export interface CompanionPlanFeedItem {
  id: number
  title: string
  status: string
  statusDisplay: string
  materialsConfirmed: boolean
  timeLocationKnown: boolean
  needsCompanion: boolean
  updatedAt: string
}

export type RepeatCycle = 'once' | 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'weekdays' | 'weekends'

export type ListeningStatus = 'pending' | 'listened' | 'skipped' | 'want_excerpt'

export interface ListeningSchedule {
  id: number
  programName: string
  startDate: string
  endDate: string | null
  repeatCycle: RepeatCycle
  repeatCycleDisplay: string
  repeatWeekdays: string | null
  broadcastTime: string
  channelSource: string
  reminderAdvanceMinutes: number
  reminderAdvanceMinutesDisplay: string
  suitableListeners: UserInfo[]
  suitableListenerIds?: number[]
  remark: string | null
  isActive: boolean
  createdBy: UserInfo | null
  createdByName: string
  recordCountToday: number
  createdAt: string
  updatedAt: string
}

export interface ListeningRecord {
  id: number
  schedule: ListeningSchedule | null
  scheduleId?: number
  listenDate: string
  status: ListeningStatus
  statusDisplay: string
  listener: UserInfo | null
  listenerName: string
  note: string | null
  excerptDraftId: number | null
  statusUpdatedAt: string | null
  createdAt: string
  generatedExcerptDraft?: ListeningExcerptDraft | null
  generatedFollowup?: FollowUpItem | null
}

export interface ListeningExcerptDraft {
  id: number
  schedule: ListeningSchedule | null
  scheduleId?: number
  listenDate: string
  programName: string
  timeSlot: string
  contentSummary: string | null
  elderlyNotes: string | null
  topic: Topic | null
  topicId?: number | null
  channelSource: string | null
  createdBy: UserInfo | null
  excerpt: ProgramExcerpt | null
  excerptId: number | null
  isCompleted: boolean
  statusDisplay: string
  createdAt: string
  updatedAt: string
  convertedExcerpt?: ProgramExcerpt | null
}

export interface ConsecutiveMissedItem {
  scheduleId: number
  programName: string
  channelSource: string
  broadcastTime: string
  listenerId: number
  listenerName: string
  listenerAvatar: string | null
  streakCount: number
  latestListenDate: string | null
}

export interface ListeningScheduleStats {
  totalSchedules: number
  activeSchedules: number
  todayTotal: number
  todayPending: number
  todayListened: number
  weekTotal: number
  weekListened: number
  completionRate: number
  consecutiveSkipped: ConsecutiveMissedItem[]
  channelDistribution: { channel: string; count: number }[]
}

export interface FollowUpItem {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  statusDisplay: string
  priority: 'high' | 'medium' | 'low'
  priorityDisplay: string
  sourceType: 'manual' | 'confirmation' | 'review_package' | 'companion_plan' | 'companion_material' | 'listening_missed'
  sourceTypeDisplay: string
  excerpt: ProgramExcerpt | null
  excerptId?: number | null
  reviewPackageItem: ReviewPackageItem | null
  reviewPackageItemId?: number | null
  companionPlan: CompanionPlan | null
  companionPlanId?: number | null
  listeningSchedule: ListeningSchedule | null
  listeningScheduleId?: number | null
  listeningRecord: ListeningRecord | null
  listeningRecordId?: number | null
  reviewPackage: { id: number; title: string } | null
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
  popularPrograms: { programName: string; count: number }[]
  topicDistribution: { name: string; count: number; color: string }[]
  duplicateRatio: { total: number; duplicates: number; rate: number }
  unconfirmedExcerpts: number
  pendingFollowups: number
  totalExcerpts: number
  confirmationStatus: { pending: number; confirmed: number; needsVerification: number }
  pendingConfirmationCount: number
  confirmationTrend7d: { date: string; count: number }[]
  reviewPackageStats: ReviewPackageStats
  companionPlanStats: CompanionPlanStats
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

export type FeedItem =
  | { type: 'excerpt'; data: ProgramExcerpt; confirmationInfo?: ConfirmationInfo; createdAt: string }
  | { type: 'review_package'; data: ReviewPackage; createdAt: string }
  | { type: 'review_package_feedback'; data: ReviewPackageFeedItem; createdAt: string }
  | { type: 'companion_plan'; data: CompanionPlan; activityInfo?: CompanionPlanFeedItem; createdAt: string }
  | { type: 'listening_schedule'; data: ListeningSchedule; createdAt: string }
  | { type: 'listening_record'; data: ListeningRecord; createdAt: string }
  | { type: 'listening_draft'; data: ListeningExcerptDraft; createdAt: string }
