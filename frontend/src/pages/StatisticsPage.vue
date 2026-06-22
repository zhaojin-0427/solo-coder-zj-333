<template>
  <div class="page-container">
    <h1 class="page-title">
      <span>📊</span>
      <span>数据统计</span>
      <el-button
        type="primary"
        size="large"
        class="ml-auto"
        :loading="exporting"
        @click="handleExport"
      >
        📥 导出报告
      </el-button>
    </h1>

    <div v-if="loading" class="loading-container py-16">
      <div class="text-gray-500 text-lg">⏳ 加载中...</div>
    </div>

    <div v-else>
      <el-row :gutter="24" class="mb-6">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number">{{ statistics?.totalExcerpts || 0 }}</div>
            <div class="stat-label">📋 总摘录数</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-blue">{{ statistics?.duplicateRatio?.duplicates || 0 }}</div>
            <div class="stat-label">⚠️ 重复记录</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-yellow">{{ statistics?.confirmationStatus?.pending || 0 }}</div>
            <div class="stat-label">⏳ 待确认</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-green">{{ statistics?.confirmationStatus?.confirmed || 0 }}</div>
            <div class="stat-label">✅ 已确认</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24" class="mb-6">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-purple">{{ statistics?.reviewPackageStats?.totalPackages || 0 }}</div>
            <div class="stat-label">📚 资料包数量</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-orange">{{ statistics?.reviewPackageStats?.totalItems || 0 }}</div>
            <div class="stat-label">📄 资料包条目</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-yellow">{{ statistics?.reviewPackageStats?.highlightedItems || 0 }}</div>
            <div class="stat-label">⭐ 重点标记</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-red-500">{{ statistics?.reviewPackageStats?.needsExplanationCount || 0 }}</div>
            <div class="stat-label">❓ 待讲解</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24" class="mb-6">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-orange">{{ statistics?.companionPlanStats?.totalPlans || 0 }}</div>
            <div class="stat-label">🤝 陪办计划总数</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-green">{{ materialPreparedPercent }}%</div>
            <div class="stat-label">✅ 材料准备完成率</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-yellow">{{ statistics?.companionPlanStats?.pending7d || 0 }}</div>
            <div class="stat-label">⏰ 近7天待办理</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-purple">{{ statistics?.companionPlanStats?.topLocations?.length || 0 }}</div>
            <div class="stat-label">📍 高频办理地点数</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24" class="mb-6">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-blue">{{ listeningStats?.totalSchedules || 0 }}</div>
            <div class="stat-label">📅 日程总数</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-yellow">{{ listeningStats?.todayPending || 0 }}</div>
            <div class="stat-label">⏰ 今日待收听</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-green">{{ listeningCompletionRate }}%</div>
            <div class="stat-label">✅ 收听完成率</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-red-500">{{ listeningStats?.consecutiveSkipped?.length || 0 }}</div>
            <div class="stat-label">🔥 连续跳过栏目</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📻 高频收听栏目 TOP 10</h3>
            </template>
            <div ref="barChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📁 专题内容分布</h3>
            </template>
            <div ref="pieChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">🔄 重复记录比例</h3>
            </template>
            <div ref="donutChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📝 确认状态分布</h3>
            </template>
            <div class="space-y-6 py-4">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-lg font-medium">⏳ 待确认</span>
                  <span class="text-xl font-bold text-yellow">
                    {{ statistics?.confirmationStatus?.pending || 0 }}
                  </span>
                </div>
                <div class="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :style="{
                      width: `${pendingPercent}%`,
                      backgroundColor: '#FAAD14'
                    }"
                  ></div>
                </div>
                <p class="text-right text-sm text-gray-500 mt-1">{{ pendingPercent }}%</p>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-lg font-medium">✅ 已确认</span>
                  <span class="text-xl font-bold text-green">
                    {{ statistics?.confirmationStatus?.confirmed || 0 }}
                  </span>
                </div>
                <div class="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :style="{
                      width: `${confirmedPercent}%`,
                      backgroundColor: '#52C41A'
                    }"
                  ></div>
                </div>
                <p class="text-right text-sm text-gray-500 mt-1">{{ confirmedPercent }}%</p>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-lg font-medium">❗ 需核实</span>
                  <span class="text-xl font-bold text-red-500">
                    {{ statistics?.confirmationStatus?.needsVerification || 0 }}
                  </span>
                </div>
                <div class="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :style="{
                      width: `${needsVerificationPercent}%`,
                      backgroundColor: '#F5222D'
                    }"
                  ></div>
                </div>
                <p class="text-right text-sm text-gray-500 mt-1">{{ needsVerificationPercent }}%</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📈 近 7 天待确认趋势</h3>
            </template>
            <div ref="trendChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📊 确认状态总览</h3>
            </template>
            <div ref="confirmationPieRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📚 资料包专题分布</h3>
            </template>
            <div ref="packageTopicChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">💬 老人反馈分布</h3>
            </template>
            <div ref="feedbackChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">🤝 陪办计划状态分布</h3>
            </template>
            <div ref="companionStatusChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📍 高频办理地点 TOP 5</h3>
            </template>
            <div ref="topLocationsChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">📺 各频道订阅分布</h3>
            </template>
            <div ref="channelChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">🔥 连续跳过栏目列表</h3>
            </template>
            <div v-if="!listeningStats?.consecutiveSkipped?.length" class="py-8">
              <el-empty description="暂无连续跳过的栏目" :image-size="80" />
            </div>
            <div v-else class="space-y-3 max-h-80 overflow-y-auto">
              <div
                v-for="item in listeningStats.consecutiveSkipped"
                :key="`${item.scheduleId}-${item.listenerId}`"
                class="p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-medium text-red-700">📻 {{ item.programName }}</span>
                  <el-tag type="danger" size="small" effect="light">
                    跳过 {{ item.streakCount }} 次
                  </el-tag>
                </div>
                <div class="flex flex-wrap gap-3 text-sm text-gray-600">
                  <span>📺 {{ item.channelSource }}</span>
                  <span>⏰ {{ item.broadcastTime }}</span>
                  <span>👤 {{ item.listenerName }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import type { Statistics, ListeningScheduleStats } from '@/types'
import { statisticsApi, scheduleApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const exporting = ref(false)
const statistics = ref<Statistics | null>(null)
const listeningStats = ref<ListeningScheduleStats | null>(null)

const barChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)
const donutChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const confirmationPieRef = ref<HTMLElement | null>(null)
const packageTopicChartRef = ref<HTMLElement | null>(null)
const feedbackChartRef = ref<HTMLElement | null>(null)
const companionStatusChartRef = ref<HTMLElement | null>(null)
const topLocationsChartRef = ref<HTMLElement | null>(null)
const channelChartRef = ref<HTMLElement | null>(null)

let barChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let donutChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let confirmationPie: echarts.ECharts | null = null
let packageTopicChart: echarts.ECharts | null = null
let feedbackChart: echarts.ECharts | null = null
let companionStatusChart: echarts.ECharts | null = null
let topLocationsChart: echarts.ECharts | null = null
let channelChart: echarts.ECharts | null = null

const totalConfirmation = computed(() => {
  if (!statistics.value?.confirmationStatus) return 0
  const { pending, confirmed, needsVerification } = statistics.value.confirmationStatus
  return pending + confirmed + needsVerification
})

const pendingPercent = computed(() => {
  if (totalConfirmation.value === 0) return 0
  return Math.round((statistics.value?.confirmationStatus?.pending || 0) / totalConfirmation.value * 100)
})

const confirmedPercent = computed(() => {
  if (totalConfirmation.value === 0) return 0
  return Math.round((statistics.value?.confirmationStatus?.confirmed || 0) / totalConfirmation.value * 100)
})

const needsVerificationPercent = computed(() => {
  if (totalConfirmation.value === 0) return 0
  return Math.round((statistics.value?.confirmationStatus?.needsVerification || 0) / totalConfirmation.value * 100)
})

const materialPreparedPercent = computed(() => {
  return Math.round((statistics.value?.companionPlanStats?.materialPreparedRate || 0) * 100)
})

const listeningCompletionRate = computed(() => {
  return Math.round((listeningStats.value?.completionRate || 0) * 100)
})

const initBarChart = () => {
  if (!barChartRef.value || !statistics.value) return

  if (barChart) {
    barChart.dispose()
  }

  barChart = echarts.init(barChartRef.value)

  const data = statistics.value.popularPrograms || []
  const names = data.map(item => item.programName)
  const counts = data.map(item => item.count)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        fontSize: 14,
        rotate: 30,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '收听次数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#FF9966' },
            { offset: 1, color: '#FF7A45' }
          ]),
          borderRadius: [8, 8, 0, 0]
        },
        barWidth: '50%',
        label: {
          show: true,
          position: 'top',
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    ]
  }

  barChart.setOption(option)
}

const initPieChart = () => {
  if (!pieChartRef.value || !statistics.value) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)

  const data = statistics.value.topicDistribution || []

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '专题分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data.map(item => ({
          value: item.count,
          name: item.name,
          itemStyle: {
            color: item.color
          }
        }))
      }
    ]
  }

  pieChart.setOption(option)
}

const initDonutChart = () => {
  if (!donutChartRef.value || !statistics.value) return

  if (donutChart) {
    donutChart.dispose()
  }

  donutChart = echarts.init(donutChartRef.value)

  const { total, duplicates, rate } = statistics.value.duplicateRatio || { total: 0, duplicates: 0, rate: 0 }
  const unique = total - duplicates

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '重复比例',
        type: 'pie',
        radius: ['50%', '75%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 3
        },
        label: {
          show: true,
          position: 'center',
          formatter: `{a|重复率}\n{b|${(rate * 100).toFixed(1)}%}`,
          rich: {
            a: {
              fontSize: 16,
              color: '#666',
              padding: [0, 0, 8, 0]
            },
            b: {
              fontSize: 32,
              fontWeight: 'bold',
              color: '#FF7A45'
            }
          }
        },
        emphasis: {
          label: {
            show: true
          }
        },
        labelLine: {
          show: false
        },
        data: [
          {
            value: unique,
            name: '唯一记录',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#66BB6A' },
                { offset: 1, color: '#52C41A' }
              ])
            }
          },
          {
            value: duplicates,
            name: '重复记录',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#FF9966' },
                { offset: 1, color: '#FF7A45' }
              ])
            }
          }
        ]
      }
    ]
  }

  donutChart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value || !statistics.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const trendData = statistics.value.confirmationTrend7d || []
  const dates = trendData.map(item => item.date)
  const counts = trendData.map(item => item.count)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>待确认摘录：{c} 条'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        fontSize: 14
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 14
      },
      minInterval: 1
    },
    series: [
      {
        name: '待确认摘录',
        type: 'line',
        data: counts,
        smooth: true,
        itemStyle: {
          color: '#FAAD14'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#FAAD14' },
            { offset: 1, color: '#FF7A45' }
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(250, 173, 20, 0.3)' },
            { offset: 1, color: 'rgba(250, 173, 20, 0.05)' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          fontSize: 14,
          fontWeight: 'bold',
          color: '#FAAD14'
        }
      }
    ]
  }

  trendChart.setOption(option)
}

const initConfirmationPie = () => {
  if (!confirmationPieRef.value || !statistics.value) return

  if (confirmationPie) {
    confirmationPie.dispose()
  }

  confirmationPie = echarts.init(confirmationPieRef.value)

  const cs = statistics.value.confirmationStatus || { pending: 0, confirmed: 0, needsVerification: 0 }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '确认状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c} 条',
          fontSize: 14
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          {
            value: cs.pending,
            name: '待确认',
            itemStyle: {
              color: '#FAAD14'
            }
          },
          {
            value: cs.confirmed,
            name: '已确认',
            itemStyle: {
              color: '#52C41A'
            }
          },
          {
            value: cs.needsVerification,
            name: '需核实',
            itemStyle: {
              color: '#F5222D'
            }
          }
        ]
      }
    ]
  }

  confirmationPie.setOption(option)
}

const initPackageTopicChart = () => {
  if (!packageTopicChartRef.value || !statistics.value) return

  if (packageTopicChart) {
    packageTopicChart.dispose()
  }

  packageTopicChart = echarts.init(packageTopicChartRef.value)

  const data = statistics.value.reviewPackageStats?.topicDistribution || []

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '资料包专题分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data.length > 0 ? data.map(item => ({
          value: item.count,
          name: `${item.icon} ${item.name}`,
          itemStyle: {
            color: item.color
          }
        })) : [{ value: 0, name: '暂无数据', itemStyle: { color: '#ccc' } }]
      }
    ]
  }

  packageTopicChart.setOption(option)
}

const initFeedbackChart = () => {
  if (!feedbackChartRef.value || !statistics.value) return

  if (feedbackChart) {
    feedbackChart.dispose()
  }

  feedbackChart = echarts.init(feedbackChartRef.value)

  const fd = statistics.value.reviewPackageStats?.feedbackDistribution || { read: 0, reviewAgain: 0, needsExplanation: 0 }
  const total = fd.read + fd.reviewAgain + fd.needsExplanation

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '老人反馈',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 3
        },
        label: {
          show: true,
          position: 'center',
          formatter: `{a|总反馈}\n{b|${total} 条}`,
          rich: {
            a: {
              fontSize: 16,
              color: '#666',
              padding: [0, 0, 8, 0]
            },
            b: {
              fontSize: 32,
              fontWeight: 'bold',
              color: '#FF7A45'
            }
          }
        },
        emphasis: {
          label: {
            show: true
          }
        },
        labelLine: {
          show: false
        },
        data: [
          {
            value: fd.read,
            name: '✅ 已读',
            itemStyle: {
              color: '#52C41A'
            }
          },
          {
            value: fd.reviewAgain,
            name: '🔄 还想再看',
            itemStyle: {
              color: '#FAAD14'
            }
          },
          {
            value: fd.needsExplanation,
            name: '❓ 需要讲解',
            itemStyle: {
              color: '#F5222D'
            }
          }
        ]
      }
    ]
  }

  feedbackChart.setOption(option)
}

const initCompanionStatusChart = () => {
  if (!companionStatusChartRef.value || !statistics.value) return

  if (companionStatusChart) {
    companionStatusChart.dispose()
  }

  companionStatusChart = echarts.init(companionStatusChartRef.value)

  const sd = statistics.value.companionPlanStats?.statusDistribution || {
    pending: 0,
    preparing: 0,
    scheduled: 0,
    completed: 0,
    cancelled: 0
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个 ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '陪办计划状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c} 个',
          fontSize: 14
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          {
            value: sd.pending,
            name: '待办理',
            itemStyle: {
              color: '#FAAD14'
            }
          },
          {
            value: sd.preparing,
            name: '准备中',
            itemStyle: {
              color: '#1890FF'
            }
          },
          {
            value: sd.scheduled,
            name: '已预约',
            itemStyle: {
              color: '#722ED1'
            }
          },
          {
            value: sd.completed,
            name: '已完成',
            itemStyle: {
              color: '#52C41A'
            }
          },
          {
            value: sd.cancelled,
            name: '已取消',
            itemStyle: {
              color: '#999999'
            }
          }
        ]
      }
    ]
  }

  companionStatusChart.setOption(option)
}

const initTopLocationsChart = () => {
  if (!topLocationsChartRef.value || !statistics.value) return

  if (topLocationsChart) {
    topLocationsChart.dispose()
  }

  topLocationsChart = echarts.init(topLocationsChartRef.value)

  const data = statistics.value.companionPlanStats?.topLocations || []
  const locations = data.map(item => item.location).reverse()
  const counts = data.map(item => item.count).reverse()

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c} 次'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 14
      },
      minInterval: 1
    },
    yAxis: {
      type: 'category',
      data: locations,
      axisLabel: {
        fontSize: 14
      }
    },
    series: [
      {
        name: '办理次数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#FF9966' },
            { offset: 1, color: '#FF7A45' }
          ]),
          borderRadius: [0, 8, 8, 0]
        },
        barWidth: '50%',
        label: {
          show: true,
          position: 'right',
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    ]
  }

 topLocationsChart.setOption(option)
}

const initChannelChart = () => {
  if (!channelChartRef.value || !listeningStats.value) return

  if (channelChart) {
    channelChart.dispose()
  }

  channelChart = echarts.init(channelChartRef.value)

  const data = listeningStats.value.channelDistribution || []

  const colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc"]

  const option = {
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} 个 ({d}%)"
    },
    legend: {
      orient: "vertical",
      right: "5%",
      top: "center",
      itemWidth: 20,
      itemHeight: 20,
      textStyle: {
        fontSize: 14
      }
    },
    series: [
      {
        name: "雱队师�!�",
        type: "pie",
        radius: ["40%", "70%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2
        },
        label: {
          show: false,
          position: "center"
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: "bold"
          }
        },
        labelLine: {
          show: false
        },
        data: data.length > 0 ? data.map((item, index) => ({
          value: item.count,
          name: item.channel,
          itemStyle: {
            color: colors[index % colors.length]
          }
        })) : [{ value: 0, name: "是札数据", itemStyle: { color: "#ccc" } }]
      }
    ]
  };

  channelChart.setOption(option)
}

const initCharts = () => {
  nextTick(() => {
    initBarChart()
    initPieChart()
    initDonutChart()
    initTrendChart()
    initConfirmationPie()
    initPackageTopicChart()
    initFeedbackChart()
    initCompanionStatusChart()
    initTopLocationsChart()
    initChannelChart()
  })
}

const loadStatistics = async () => {
  loading.value = true
  try {
    [statistics.value, listeningStats.value] = await Promise.all([
      statisticsApi.getStatistics(),
      scheduleApi.getStats()
    ]) 
    initCharts()
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

const handleResize = () => {
  barChart?.resize()
  pieChart?.resize()
  donutChart?.resize()
  trendChart?.resize()
  confirmationPie?.resize()
  packageTopicChart?.resize()
  feedbackChart?.resize()
  companionStatusChart?.resize()
  topLocationsChart?.resize()
  channelChart?.resize()
}

watch(
  () => statistics.value,
  () => {
    if (statistics.value) {
      initCharts()
    }
  }
)

onMounted(() => {
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  pieChart?.dispose()
  donutChart?.dispose()
  trendChart?.dispose()
  confirmationPie?.dispose()
  packageTopicChart?.dispose()
  feedbackChart?.dispose()
  companionStatusChart?.dispose()
  topLocationsChart?.dispose()
  channelChart?.dispose()
})
</script>
