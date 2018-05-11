<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{modelCount}}</span>
            </Strong>
          </div>
        </div>
        <my-table :tableData="tableData"></my-table>
      </el-card>
    </div>
    <div>
      <el-dialog
        :title="dialogTitle"
        :visible.sync="dialogVisible"
        width="30%">
        <vue-json-pretty :data="detail"></vue-json-pretty>
        <span slot="footer" class="dialog-footer">
      </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>

import ajax from '../request/index'
import myTable from '../components/Table'
import VueJsonPretty from 'vue-json-pretty'

export default {
  name: 'model_templates',
  components: {myTable, VueJsonPretty},
  data() {
    return {
      modelCount: 0,
      dialogVisible: false,
      dialogTitle: '',
      detail: null,
      tableData: {
        label: ["ID", 'Name'],
        prop: ['id', 'name'],
        list: [],
        handleDetailClick: function (row) {
          if (row == null) {
            return
          }

          this.dialogVisible = true;
          this.dialogTitle = row.name;
          // row.config = JSON.parse(JSON.stringify(row.config));
          // console.log(row.config);
          row.config =  eval("(" + row.config + ')');
          this.detail = row;
        }.bind(this)
      }
    }
  },

  created() {
    ajax.getModelTemplates().then((result) => {
      this.tableData.list = result.data.data;
      this.modelCount = this.tableData.list.length;
    }).catch(() => {});
  }
}
</script>
