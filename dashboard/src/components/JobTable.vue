<template>
  <div>
    <el-table ref="singleTable" :data="data.list" highlight-current-row style="width: 100%">
      <el-table-column v-for="(item, index) in data.prop" :key="index"
      :prop="item" :label="data.label[index]">
      </el-table-column>
      <el-table-column
      fixed="right"
      label="operation"
      width="100">
      <template slot-scope="scope">
        <el-button @click="handleDetailClick(scope.row)" type="text" size="small">
          detail
        </el-button>
        <el-button @click="handleStopClick(scope.row)" type="text" size="small">
         stop
        </el-button>
      </template>
    </el-table-column>
    </el-table>
  </div>
</template>
<script>
  import ajax from '../request/index'
  export default {
    name: 'job-table',
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
      handleDetailClick(row) {
        this.tableData.handleDetailClick(row);
      },
      handleStopClick(row) {
        this.tableData.handleStopClick(row);
      }
    }
  }

</script>
<style lang="scss">


</style>
