fp = "src/pages/StatisticsPage.vue"
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

old = """            <div v-else class="space-y-3 max-h-80 overflow-y-auto">
      </el-row>"""
print("Found old:", old in c)

new = """            <div v-else class="space-y-3 max-h-80 overflow-y-auto">
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
      </el-row>"""

if old in c:
    c = c.replace(old, new)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)
    print("Replaced successfully!")
else:
    print("Pattern not found")
