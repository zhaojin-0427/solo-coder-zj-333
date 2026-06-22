const fs = require("fs");
const fp = "src/pages/StatisticsPage.vue";
let c = fs.readFileSync(fp, "utf8");
const oldStr = "  topLocationsChart.setOption(option)\n}\n\nconst initCharts = () => {";
const addStr = ` topLocationsChart.setOption(option)
}

const initChannelChart = () => {
  if (!hannelChartRef.value || !listeningStats.value) return

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

const initCharts = () => {`;

if (c.includes(oldStr)) {
  c = c.replace(oldStr, addStr);
  fs.writeFileSync(fp, c);
  console.log("initChannelChart added!");
} else {
  console.log("Pattern not found");
}