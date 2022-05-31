<template>
  <div class="dashboard p-4 heigth_pass">
    <nav class="flex" aria-label="Breadcrumb">
      <ol class="inline-flex items-center space-x-1 md:space-x-3">
        <li class="inline-flex items-center">
          <a
            href="#"
            class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            <svg
              class="mr-2 w-4 h-4"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
              ></path>
            </svg>
            Dashboard
          </a>
        </li>
      </ol>
    </nav>
    <!-- end nav -->
    <div class="chart">
      <v-chart class="chart" :option="option" autoresize :loading="loading" />
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import { Icon } from "@iconify/vue";
import VChart from "vue-echarts";
import axios from "axios";

export default {
  name: "Dashboard",
  components: {
    VChart,
  },
  data() {
    return { option: null, loading: true };
  },
  mounted() {
    axios
      .get('http://' + process.env.VUE_APP_DF + '/tree')
      .then((response) => {
        var raw_graph = response.data;
        console.log(raw_graph);
        var graph = {
          'nodes': [],
          'links': [],
          'categories': []
        }
        raw_graph.nodes.forEach(function (node) {
          var group_size = raw_graph.node_members[node[0]]
          graph.nodes.push({
            "id": node[0],
            "name": node[0],
            "category": node[1],
            "label": {
              show: node[1] == "level0",
            },
            "symbolSize": (group_size + 1) * 10,
            "value": group_size
          })
        })
        raw_graph.links.forEach(function (link) {
          graph.links.push({
            "source": link[0],
            "target": link[1]
          })
        })
        raw_graph.categories.sort()
        raw_graph.categories.forEach(function (category) {
          graph.categories.push({
            'name': category
          })
        })
        
        this.option = {
          title: {
            text: "Multi-Agent Ecosystem",
            subtext: "",
            top: "bottom",
            left: "right",
          },
          tooltip: {},
          legend: [
            {
              data: graph.categories.map(function (a) {
                return a.name;
              }),
            },
          ],
          animationDuration: 1500,
          animationEasingUpdate: "quinticInOut",
          series: [
            {
              name: "Info",
              type: "graph",
              layout: "force",
              data: graph.nodes,
              links: graph.links,
              categories: graph.categories,
              roam: true,
              label: {
                position: "right",
                formatter: "{b}",
              },
              lineStyle: {
                color: "source",
                curveness: 0.3,
              },
              emphasis: {
                focus: "adjacency",
                lineStyle: {
                  width: 10,
                },
              },
              force: {
                repulsion: 100,
              },
            },
          ],
        };

        this.loading = false;
      });
  },
  components: {
    Icon,
  },
};
</script>

<style scoped>
.chart {
  height: 100%;
}

.heigth_pass {
  height: 98vh;
}
</style>
