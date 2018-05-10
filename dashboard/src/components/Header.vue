<template>
  <div>
    <div class="header">
      <h1 class="title">
        Oasis Dashboard
      </h1>
      <!--<span>Oasis Dashboard</span>-->
    </div>

    <el-tabs v-model="activeIndex" type="card" @tab-click="tabClick">
      <el-tab-pane label="Job View" name="home"></el-tab-pane>
      <el-tab-pane label="Job Detail" name="detail"></el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
  export default {
    name: 'header',
    data() {
      let activeIndex = '1';
      location.hash && (activeIndex = location.hash.slice(2));
      return {
        activeIndex
      };
    },
    methods: {
      tabClick(tab) {
        let path = this.activeIndex;
        this.$router.push({
          path: path
        });
      },
    }
  };

</script>

<style scoped>
  .header {
    display: flex;
    align-items: baseline;
    width: 80rem;
  }

  .title {
    margin-right: 25px;
  }

</style>
