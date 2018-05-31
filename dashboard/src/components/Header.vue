<template>
<div>
  <div class="header">
    <h1 class="title">
        Oasis Dashboard
      </h1>
    <!--<span>Oasis Dashboard</span>-->
  </div>
  <el-tabs :value="activeIndex" type="card" @tab-click="tabClick">
      <el-tab-pane label="Job View" name="home"></el-tab-pane>
      <el-tab-pane label="Job Detail" name="detail"></el-tab-pane>
      <el-tab-pane label="Model Templates View" name="model_templates"></el-tab-pane>
  </el-tabs>

</div>
</template>
<script>
export default {
    data() {
      let activeIndex = 'home';
      console.log('url is ', window.location.href);
      if((window.location.href).includes('detail')) {
        activeIndex = 'detail'
      }


      return {
        activeIndex
      };
    },
    methods: {
      tabClick(tab) {
        console.log('tab name', tab.name)
        console.log('this.activeIndex', this.activeIndex)
        let path = tab.name;
        console.log('path is ', path);
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
