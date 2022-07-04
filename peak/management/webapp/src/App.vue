<template>
  <!-- App -->
  <div class="flex bg-packed font-lexend">
    <transition name="fade">
      <div
        id="sidebar-scroll"
        class="flex-sidebar lg:flex-auto w-sidebar lg:block hidden bg-white border-r-2 h-screen lg:z-0 z-40 overflow-auto lg:relative fixed"
      >
        <Sidebar />
      </div>
    </transition>
    <div class="flex-auto w-full overflow-auto h-screen" id="body-scroll">
      <router-view />
    </div>
  </div>
  <!-- end app -->
</template>

<script>
  // vue Components
  import Sidebar from "@/components/Sidebar";
  // npm-js
  import Scrollbar from "smooth-scrollbar";
  export default {
    name: "App",
    components: {
      Sidebar,
    },
    mounted() {
      Scrollbar.init(document.querySelector("#body-scroll"));

      setTimeout(() => {
        var alert_dis = document.querySelectorAll(".alert-dismiss");
        alert_dis.forEach((x) =>
          x.addEventListener("click", function () {
            x.parentElement.classList.add("hidden");
          })
        );
      }, 100);
    },
  };
</script>
