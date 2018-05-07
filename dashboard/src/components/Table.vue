<template>
  <div>
    <el-table ref="singleTable" :data="data.list" highlight-current-row 
    @current-change="handleCurrentChange" style="width: 100%">
      <el-table-column v-for="(item, index) in data.prop" :key="index" 
      :prop="item" :label="data.label[index]">
      </el-table-column>
    </el-table>
  </div>
</template>
<script>
  export default {
    name: 'sh-table',
    props: ['tableData'],
    data() {
      return {
        data: this.tableData
      }
    },
    methods: {
      setCurrent(row) {
        this.$refs.singleTable.setCurrentRow(row);
      },
      handleCurrentChange(val) {
        this.currentRow = val;
        this.tableData.handleClick(val);
      }
    }
  }

</script>
<style lang="scss">


</style>
