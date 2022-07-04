<template>
  <!-- sidebar -->
  <nav class="sidebar">
    <!-- sidebar head -->
    <div class="sidebar-head p-4">
      <router-link to="/" exact>
        <h2 class="text-2xl font-normal text-gray-800" translate="no">
          PEAK<span class="text-primary">.</span>
        </h2>
      </router-link>
      <button class="lg:hidden block float-right -mt-7" @click="sidebarToggle">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          role="img"
          width="25px"
          height="25px"
          preserveAspectRatio="xMidYMid meet"
          viewBox="0 0 32 32"
        >
          <path
            fill="currentColor"
            d="M7.219 5.781L5.78 7.22L14.563 16L5.78 24.781l1.44 1.439L16 17.437l8.781 8.782l1.438-1.438L17.437 16l8.782-8.781L24.78 5.78L16 14.563z"
          />
        </svg>
      </button>
    </div>

    <!-- sidebar list -->
    <div class="sidebar-list p-4 mt-4">
      <p class="font-medium text-gray-400">Menu</p>
      <div class="wrap-item mt-4">
        <div class="item">
          <router-link
            to="/"
            exact
            class="w-full flex text-left rounded-md box-border p-3"
          >
            <span class="mr-3 text-xl"><Icon icon="ph:graph-duotone" /></span>
            <span class="w-full"> Ecosystem </span>
          </router-link>
        </div>
        <div class="item mt-3">
          <menu-accordion>
            <template v-slot:icon>
              <Icon icon="gg:chart" />
            </template>
            <template v-slot:title> Data Analysis </template>
            <template v-slot:content>
              <router-link
                to="/data/visualization"
                class="w-full text-left block rounded-md p-3 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Data Visualization
              </router-link>
              <router-link
                to="/data/customization"
                class="w-full text-left block rounded-md p-3 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Chart Customization
              </router-link>
            </template>
          </menu-accordion>
        </div>
        
      </div>
      
    </div>
  </nav>
</template>

<script>
  import { Icon } from "@iconify/vue";
  import MenuAccordion from "./MenuAccordion.vue";
  export default {
    components: {
      Icon,
      MenuAccordion,
    },
    methods: {
      sidebarToggle: function () {
        document.querySelector(".flex-sidebar").classList.add("hidden");
      },
    },
    mounted() {},
  };
</script>
