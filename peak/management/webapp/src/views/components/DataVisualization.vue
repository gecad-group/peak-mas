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
    <div class="wrapper-card grid lg:grid-cols-4 grid-cols-1 md:grid-cols-2 gap-2 mt-5 h-96">
      <!-- card  -->
        <div class="card bg-white dark:bg-gray-800 w-full rounded-md p-5 shadow flex">
          <v-chart
            :option="chartsOptions[0]"
            autoresize
          />
        </div>
      <!-- end card -->
    </div>
    <!-- end wrapper card -->
  </div>
<!-- end wrapper card
  <div
    v-for="i in Math.floor(nCharts/4)+((nCharts % 4 > 0) ? 1 : 0)"
    class="wrapper-card grid lg:grid-cols-4 grid-cols-1 md:grid-cols-2 gap-2 mt-5"
  >
    <template v-if="i < Math.floor(nCharts/4)+((nCharts % 4 > 0) ? 1 : 0)">
      <div
        v-for="j in 4"
        class="card bg-white dark:bg-gray-800 w-full rounded-md p-5 shadow flex h-full"
      >
        <v-chart
          :option="chartsOptions[(i - 1) * nCharts + j - 1]"
          autoresize
        />
      </div>
    </template>
    <template v-else>
      <div
        v-for="j in nCharts % 4"
        class="card bg-white dark:bg-gray-800 w-full rounded-md p-5 shadow flex"
      >
        <v-chart
          :option="chartsOptions[(i - 1) * nCharts + j - 1]"
          autoresize
        />
      </div>
    </template>
  </div>-->
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
      chartsOptions: [],
      nCharts: 0,
      previous_data: null,
      timer: "",
    };
  },
  methods: {
    fetchGraph() {
      axios
        .get("http://" + process.env.VUE_APP_DF + "/dataanalysis")
        .then((response) => {
          var data = JSON.stringify(response.data)
          if (data != this.previous_data) {
            this.previous_data = data;
            this.renderCharts(response.data);
          }
        });
    },
    renderCharts(raw_charts) {
      this.chartsOptions = [];
      var options = {};
      Object.keys(raw_charts).forEach((chart_name) => {
        if (
          raw_charts[chart_name].graph_options != null ||
          raw_charts[chart_name].graph_options != ""
        ) {
          options = {
            title: {
              text: chart_name
            },
            tooltip: {
              trigger: 'axis'
            },
            xAxis: {
              type: 'value'
            },
            yAxis: {
              type: 'value'
            },
            series: []
          }
          Object.keys(raw_charts[chart_name]['data']).forEach((data_array)=>{
            options.series.push({
                data: raw_charts[chart_name]['data'][data_array],
                type: 'line',
                smooth: true
              })
            options.xAxis['data'] = [...Array(raw_charts[chart_name]['data'][data_array].length).keys()]
            console.log(raw_charts[chart_name]['data'][data_array].length)
          },this)
        } else {
          options = raw_charts[chart_name]['graph_options']
        }
        console.log(options)
        this.chartsOptions.push(options)
      }, this);
      this.nCharts = this.chartsOptions.length
    },
  },
  mounted() {
    this.fetchGraph();
    this.timer = setInterval(this.fetchGraph, 5000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
};
</script>
