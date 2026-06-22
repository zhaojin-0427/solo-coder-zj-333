import sys
fp = "src/pages/StatisticsPage.vue"
with open(fp, "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines:", len(lines))
for i, line in enumerate(lines[95:115], start=96):
    print(f"{i}: {line}", end="")
