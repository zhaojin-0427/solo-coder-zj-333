fp = "src/pages/StatisticsPage.vue"
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

old = "            <div v-else class=\"space-y-3 max-h-80 overflow-y-auto\">
      </el-row>"
print("Found old:", old in c)
