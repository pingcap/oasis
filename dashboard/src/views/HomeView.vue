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
            <el-button @click="">New</el-button>
          </div>
        </div>
        <my-table :tableData="tableData"></my-table>
      </el-card>
    </div>
    <div>
      <el-dialog :title="dialogData.title" :visible.sync="dialog">
        <el-form :inline="true" :model="dialogData.jobForm" :rules="dialogData.jobRules"
                 ref="dialogData.jobForm" label-width="6rem">
          <!--<el-form-item label="Name:" prop="name">-->
            <!--<el-input v-model="dialogData.missionForm.name"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="Scenes:" prop="scenes_name">-->
            <!--<el-select v-model="dialogData.missionForm.scenes_name" placeholder="select scenes">-->
              <!--<el-option v-for="(s, index) in scenes" :key="s.id" :label="s.name" :value="s.name"></el-option>-->
            <!--</el-select>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="PD Version:" prop="pd_version">-->
            <!--<el-input v-model="dialogData.missionForm.pd_version"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="TiDB Version:" prop="tidb_version">-->
            <!--<el-input v-model="dialogData.missionForm.tidb_version"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="TiKV Version:" prop="tikv_version">-->
            <!--<el-input v-model="dialogData.missionForm.tikv_version"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="Slack Channel:" prop="slack_channel">-->
            <!--<el-input v-model="dialogData.missionForm.slack_channel"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="Timeout:" prop="timeout">-->
            <!--<el-input v-model="dialogData.missionForm.timeout"></el-input>-->
          <!--</el-form-item>-->
          <!--<el-form-item label="IgnoreErrors:" prop="ignore_errors">-->
            <!--<el-input v-model="dialogData.missionForm.ignore_errors"></el-input>-->
          <!--</el-form-item>-->
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialog = false; clearMissionForm()">Cancel</el-button>
          <el-button @click="resetForm('dialogData.missionForm')">Reset</el-button>
          <el-button @click="submitForm('dialogData.missionForm', dialogData.type)">OK</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import ajax from '../request/index'
import myTable from  '../components/table'
// import router from '../router/index'

export default {
  components: {myTable},
  name: 'home',
  data() {
    return {
        jobCount: 0,
        tableData: {
           label: ['Job ID', 'Status', 'Models', 'Create Time'],
           prop: ['id', 'status', 'models', 'create_time'],
           list: [],
          handleDetailClick: function (row) {
            if (row == null) {
              return
            }

            // router.push({ name: 'JobDetailView', params: { id: row.id }})
            window.location.href='detail?id='+row.id ;
          },

          modelTemplates: [],
          dialog: false,
          dialogData: {
            title: '',
            jobForm: {
              data_source: '',
              metrics: '',
              models: []
            }
          }
       },
    }
   },
  created() {
    ajax.getJobs().then((result) => {
      this.tableData.list = result.data.data;
    }).catch(() => {})

    ajax.getModelTemplates((result) => {
      this.modelTemplates = result.data.data;
    })
  }
}
</script>
