<template>
  <div class="p-4">
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
            Ecosystem
          </a>
        </li>
        <li>
          <div class="flex items-center">
            <svg
              class="w-6 h-6 text-gray-400"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              ></path>
            </svg>
            <a
              href="#"
              class="ml-1 text-sm font-medium text-gray-700 hover:text-gray-900 md:ml-2 dark:text-gray-400 dark:hover:text-white"
              >Data Analysis</a
            >
          </div>
        </li>
        <li>
          <div class="flex items-center">
            <svg
              class="w-6 h-6 text-gray-400"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              ></path>
            </svg>
            <a
              href="#"
              class="ml-1 text-sm font-medium text-gray-700 hover:text-gray-900 md:ml-2 dark:text-gray-400 dark:hover:text-white"
              >Data Visualization</a
            >
          </div>
        </li>
      </ol>
    </nav>
    <!-- end nav -->
    <!-- grid wrapper card -->
    <div
      v-for="i in (length(this.charts) + (length(this.charts) % 4)) / 4"
      class="wrapper-card grid lg:grid-cols-4 grid-cols-1 md:grid-cols-2 gap-2 mt-5"
    >
      <!-- card  -->
      <div
        v-for="j in length(this.charts) % 4"
        class="card bg-white dark:bg-gray-800 w-full rounded-md p-5 shadow flex"
      >
        <v-chart
          :option="charts[(i - 1) * length(this.charts) + j - 1]"
          autoresize
        />
      </div>
      <!-- end card -->
    </div>
    <!-- end wrapper card -->
  </div>
</template>

<script>
import { Icon } from "@iconify/vue";
import VChart from "vue-echarts";
import axios from "axios";

export default {
  name: "Data Visualization",
  components: {
    VChart,
    Icon,
  },
  data() {
    return {
      charts: {},
      previous_data: null,
      timer: "",
      defaultOptions: {},
    };
  },
  methods: {
    fetchGraph() {
      axios
        .get("http://" + process.env.VUE_APP_DF + "/dataanalysis")
        .then((response) => {
          if (JSON.stringify(response.data) != this.previous_data) {
            this.previous_data = JSON.stringify(response.data);
            this.renderCharts(response.data);
          }
        });
    },
    renderCharts(raw_charts) {
      this.charts = {};
      raw_charts.keys().forEach((chart_name) => {
        if (
          raw_charts[chart_name].graph_options != null &&
          raw_charts[chart_name].graph_options != ""
        ) {
          raw_charts[chart_name].data.keys().forEach((data_key) => {
            raw_charts[chart_name].graph_options.replace(
              "#" + data_key,
              raw_charts[chart_name].data[data_key]
            );
          }, this);
        } else {
          this.getOptions(raw_charts[chart_name], chart_name);
        }
      }, this);
    },
    getOptions(chart, chart_name) {
      option = {
        title: {
          text: chart_name,
        },
        tooltip: {
          trigger: "axis",
        },
        legend: {
          data: [],
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            name: "Email",
            type: "line",
            stack: "Total",
            data: [120, 132, 101, 134, 90, 230, 210],
          },
          {
            name: "Union Ads",
            type: "line",
            stack: "Total",
            data: [220, 182, 191, 234, 290, 330, 310],
          },
          {
            name: "Video Ads",
            type: "line",
            stack: "Total",
            data: [150, 232, 201, 154, 190, 330, 410],
          },
          {
            name: "Direct",
            type: "line",
            stack: "Total",
            data: [320, 332, 301, 334, 390, 330, 320],
          },
          {
            name: "Search Engine",
            type: "line",
            stack: "Total",
            data: [820, 932, 901, 934, 1290, 1330, 1320],
          },
        ],
      };
      chart.data.keys().forEach((data_key) => {
        option.legend.data.appen
      }, this);
    },
  },
  mounted() {
    this.fetchGraph();
    this.loading = false;
    this.timer = setInterval(this.fetchGraph, 5000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
};
</script>
