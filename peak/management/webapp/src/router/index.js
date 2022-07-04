import { createRouter, createWebHistory } from "vue-router";

// Default Pages
import Dashboard from "../views/Dashboard.vue";
// Component Pages
import DataVisualization from "../views/components/DataVisualization.vue";
import ChartCustomization from "../views/components/ChartCustomization.vue"
var appname = "PEAK - ";

const routes = [
  // Routes
  {
    path: "/",
    name: "Ecosystem",
    component: Dashboard,
    meta: { title: appname + 'Ecosystem' },
  },

  // Components Routes
  {
    path: "/data/visualization",
    name: "Data Visualization",
    component: DataVisualization,
    meta: { title: appname + "Data Visualization" },
  },
  {
    path: "/data/customization",
    name: "Chart Customization",
    component: ChartCustomization,
    meta: { title: appname + "Chart Customization" },
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,

  linkExactActiveClass: "exact-active",
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title;
  next();
});

export default router;
