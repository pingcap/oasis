<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{jobCount}}</span>
            </Strong>
          </div>
          <div>
            <el-button @click="clickCreateJob">New</el-button>
          </div>
        </div>
        <sh-table :tableData="tableData"></sh-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import ajax from '../request/index'
import myTable from  '../components/table'
export default {
  components: {myTable},
  name: 'home',
  data() {
    return {
        activeNames: ['1'],
        jobCount: 0,
        tableData: {
           label: ['Job ID', 'Status', 'Models', 'Create Time'],
           prop: ['id', 'status', 'models', 'create_time'],
           list: [],
          handleDetailClick: function (row) {
            if (row == null) {
              return
            }
          }
       },
    }
   },
  created() {
    ajax.getJobs().then((result) => {
      this.tableData.list = result.data.data;
    }).catch(() => {})
  }
}
</script>
