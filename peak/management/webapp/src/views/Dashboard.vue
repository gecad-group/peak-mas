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
      .get("http://localhost:10000/tree")
      .then((response) => {
        this.loading = false;
        this.graph = response.data;
        this.graph.nodes.forEach(function (node) {
          node.label = {
            show: node.category == "level0",
          };
        });
        console.log(response.data);
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
              data: this.graph.categories.map(function (a) {
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
              data: this.graph.nodes,
              links: this.graph.links,
              categories: this.graph.categories,
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
      })
      .catch((e) => {
        alert(e);
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
