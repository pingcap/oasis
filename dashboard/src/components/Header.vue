<template>
  <div>
    <div class="header">
      <h1 class="title">
        Schrodinger
      </h1>
      <span>TiDB Cluster Stability Test</span>
    </div>

    <el-tabs v-model="activeIndex" type="card" @tab-click="tabClick">
      <el-tab-pane label="Daily View" name="daily"></el-tab-pane>
      <el-tab-pane label="Mission" name="mission"></el-tab-pane>
      <el-tab-pane label="Scenes" name="scenes"></el-tab-pane>
      <el-tab-pane label="Case Template" name="cases"></el-tab-pane>
      <el-tab-pane label="Cluster Template" name="cluster"></el-tab-pane>
      <el-tab-pane label="History" name="history"></el-tab-pane>
      <el-tab-pane label="Release" name="release"></el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
  export default {
    name: 'header',
    data() {
      let activeIndex = 'daily';
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
