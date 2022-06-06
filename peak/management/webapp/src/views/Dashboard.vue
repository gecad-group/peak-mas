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
    <div id="divAgentList" class="text-left rounded-md box-border p-3">
      <p>Move</p>
      <p>this</p>
      <p>DIV</p>
    </div>
    <div class="chart">
      <v-chart
        class="chart"
        :option="option"
        autoresize
        :loading="loading"
        :loadingOptions="loadingOptions"
      />
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
    Icon,
  },
  data() {
    return {
      loadingOptions: {
        text: "Loading…",
        color: "#4ea397",
        maskColor: "rgba(255, 255, 255, 0.4)",
      },
      option: null,
      loading: true,
      timer: "",
      graph: null,
      res: null,
      previous_graph: {
        nodes: [],
        links: [],
        categories: [],
        node_members: [],
      },
    };
  },
  methods: {
    getOptions() {
      return {
        title: {
          text: "Multi-Agent Ecosystem",
          subtext: "",
          top: "bottom",
          left: "right",
        },
        tooltip: {},
        legend: {
          data: this.graph.categories.map(function (a) {
            return a.name;
          }),
        },
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
    },
    compare(graph1, graph2) {
      return true;
    },
    fetchGraph() {
      axios
        .get("http://" + process.env.VUE_APP_DF + "/tree")
        .then((response) => {
          if (JSON.stringify(response.data) != this.previous_graph) {
            this.previous_graph = JSON.stringify(response.data);
            this.renderGraph(response.data);
            this.option = this.getOptions();
          }
        });
    },
    renderGraph(raw_graph) {
      this.graph = {
        nodes: [],
        links: [],
        categories: [],
      };
      raw_graph.nodes.forEach(function (node) {
        var group_size = raw_graph.node_members[node[0]].length;
        this.graph.nodes.push({
          id: node[0],
          name: node[0],
          category: node[1],
          label: {
            show: node[1] == "level0",
          },
          symbolSize: (group_size + 1) * 10,
          value: group_size,
        });
      }, this);

      raw_graph.links.forEach(function (link) {
        this.graph.links.push({
          source: link[0],
          target: link[1],
        });
      }, this);

      raw_graph.categories.sort();
      raw_graph.categories.forEach(function (category) {
        this.graph.categories.push({
          name: category,
        });
      }, this);
    },
    dragElement(elmnt) {
      var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;
      if (document.getElementById(elmnt.id + "header")) {
        // if present, the header is where you move the DIV from:
        document.getElementById(elmnt.id + "header").onmousedown =
          dragMouseDown;
      } else {
        // otherwise, move the DIV from anywhere inside the DIV:
        elmnt.onmousedown = dragMouseDown;
      }

      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
      }

      function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
      }

      function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
      }
    },
  },
  mounted() {
    this.dragElement(document.getElementById("divAgentList"));
    this.fetchGraph();
    this.loading = false;
    this.timer = setInterval(this.fetchGraph, 5000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
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
#divAgentList {
  position: absolute;
  z-index: 9;
  background-color: rgb(237 246 254);
  box-shadow: 1px 1px 5px #9ca3af;
  text-align: center;
}

#divAgentListHeader {
  padding: 10px;
  cursor: move;
  z-index: 10;
  background-color: #2196f3;
  color: #fff;
}
</style>
