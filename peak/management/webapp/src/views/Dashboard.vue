<template>
  <div class="dashboard p-4 h-screen">
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
      </ol>
    </nav>
    <!-- end nav -->
    <div
      id="divAgentList"
      class="text-center absolute z-10 rounded-md box-border shadow-xl"
      v-show="showAgentList"
    >
      <div id="divAgentListheader" class="rounded-tl-md rounded-tr-md text-white cursor-move flex" :style="{'background-color': selectedNode.color}">
        <div class="p-3 m-auto">{{selectedNode.name.toUpperCase()}} members:</div>
        <div class="rounded-tr-md hover:bg-blue-200 cursor-pointer transition-colors duration-150">
          <button class="h-full p-3" @click="closeMemberList()">
            <Icon icon="akar-icons:cross" />
          </button>
        </div>
      </div>
      <div class="font-medium p-3 bg-white rounded-bl-md rounded-br-md">
        <p v-for="member in selectedNode.members">{{member[0] + '@' + member[1] + '/' + member[2]}}</p>
      </div>
    </div>
    <div class="h-full" v-if="groupMode">
      <v-chart
        :option="optionGroup"
        autoresize
        :loading="loading"
        :loadingOptions="loadingOptions"
        @click="handleGroupClick"
      />
    </div>
    <div class="h-full" v-if="!groupMode">
      <v-chart
        :option="optionMembers"
        autoresize
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
  name: "Ecosystem",
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
      optionGroup: null,
      optionMembers: null,
      loading: true,
      groupMode: true,
      timer: "",
      graph: null,
      previous_graph: null,
      showAgentList: false,
      selectedNode: {
        members: [],
        name: '',
        color: ''
      },
    };
  },
  methods: {
    getGroupOptions() {
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
              repulsion: [100, 300],
              edgeLength: 50,
            },
          },
        ],
      };
    },
    getMemberOptions() {
      var links = []
      var categories = []
      var data = [
        {
          id: this.selectedNode.name,
          name: this.selectedNode.name,
          symbolSize: 20,
          itemStyle: {
            color: this.selectedNode.color
          }
        }
      ]
      if (this.selectedNode.name && this.selectedNode.name in this.graph.node_members){
        this.selectedNode.members = this.graph.node_members[this.selectedNode.name]
        this.selectedNode.members.forEach((raw_member) => {
          var member = raw_member[0] + "@" + raw_member[1] + "/" + raw_member[2];
          data.push({
            id: member,
            name: member,
            category: member,
            symbolSize: 10
          })
          links.push({
            source: this.selectedNode.name,
            target: member
          })
          categories.push({
            name: member
          })
        }, this)
      }
      
      return {
        title: {
          text: "Members of " + this.selectedNode.name.toUpperCase(),
          subtext: "",
          top: "bottom",
          left: "right",
        },
        animationDuration: 1500,
        animationEasingUpdate: "quinticInOut",
        series: [
          {
            name: "Info",
            type: "graph",
            layout: "force",
            data: data,
            links: links,
            categories: categories,
            roam: true,
            label: {
              position: "right",
              formatter: "{b}",
              show: true,
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
    fetchGraph() {
      axios
        .get("http://" + process.env.VUE_APP_DF + "/tree")
        .then((response) => {
          if (JSON.stringify(response.data) != this.previous_graph) {
            this.previous_graph = JSON.stringify(response.data);
            this.renderGraph(response.data);
            this.optionGroup = this.getGroupOptions(); 
            this.optionMembers = this.getMemberOptions();
          }
        });
    },
    renderGraph(raw_graph) {
      this.graph = {
        nodes: [],
        links: [],
        categories: [],
        node_members: {}
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
          value: link[2]
        });
      }, this);

      raw_graph.categories.sort();
      raw_graph.categories.forEach(function (category) {
        this.graph.categories.push({
          name: category,
        });
      }, this);

      this.graph.node_members = raw_graph.node_members;
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
    handleGroupClick(...args) {
      console.log("click from echarts", args[0]);

      if (args[0].dataType == 'node' && this.groupMode){ //if in group mode, change to member mode
        this.groupMode = false;
        this.showAgentList = true;
        this.selectedNode.name = args[0].data.name;
        this.selectedNode.color = args[0].color;
        this.optionMembers = this.getMemberOptions();
      }
    },
    closeMemberList(){
      this.showAgentList = false;
      this.groupMode = true;
      this.selectedNode = {
        members: [],
        name: '',
        color: ''
      }
      this.optionGroup = this.getGroupOptions();
    }
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
