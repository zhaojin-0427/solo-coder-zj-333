const fs = require("fs");
const fp = "src/pages/StatisticsPage.vue";
let c = fs.readFileSync(fp, "utf8");

const old2 = `       </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="; padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">👨🔷高收桥的武 TOP 10</h3>`';

const stat_cards = `        </el-col>
      </el-row>

      <el-row :gutter="24" class="mb-6">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-blue">{{ listeningStats?.totalSchedules || 0 }}</div>
            <div class="stat-label">💤 放秈怂数据</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-yellow">{{ listeningStats?.todayPending || 0 }}</div>
            <div class="stat-label">⌄🔴 个嗥数据</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-green">{{ listeningCompletionRate }%}</div>
            <div class="stat-label">✑ 版同库合纾</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-number text-red-500">{{ listeningStats?.consecutiveSkipped?.length || 0 }}</div>
            <div class="stat-label">🔥 转组行转竛慮</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="12" class="mb-6">
          <el-card class="shadow-card" :body-style="{ padding: '24px' }">
            <template #header>
              <h3 class="text-xl font-semibold">👨🔷高收桵的武 TOP 10</h3>`;

if (c.includes(old2)) {
  c = c.replace(old2, stat_cards);
  fs.writeFileSync(fp, c);
  console.log("2. Stat cards added!");
} else {
  console.log("2. Could not find stat cards insertion point");
}