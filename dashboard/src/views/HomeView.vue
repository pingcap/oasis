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
        <my-table :tableData="tableData"></my-table>
      </el-card>
    </div>
    <div>
      <el-dialog :title="dialogData.title" :visible.sync="dialog">
        <el-form :model="dialogData.jobForm"
                 ref="dialogData.jobForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="dialogData.jobForm.name" placeholder="job-1"></el-input>
          </el-form-item>
          <el-form-item label="Datasource:" prop="data_source">
            <el-input v-model="dialogData.jobForm.data_source" type="textarea" placeholder="{'url': 'xxxx'}">
            </el-input>
          </el-form-item>
          <el-form-item label="Timeout:" prop="timeout">
            <el-input v-model="dialogData.jobForm.timeout" placeholder="48h"></el-input>
          </el-form-item>
           <div class="me-models">
            <big>
              <strong>
                <span>Models: </span>
              </strong>
            </big>
            <a class="me-a" @click="addModel">Add Model</a>
          </div>
           <div v-for="(model, index) in dialogData.jobForm.models" :key="model.key">
            <div class="sch-boxes">
              <label>Model-{{index}}&nbsp;</label>
              <a class="me-a" @click="removeBox(model)"> Remove </a>
            </div>
            <el-form-item label="Name:" :prop="'models.' + index + '.name'">
              <el-select v-model="model.name" placeholder="select model template" style="width:100%">
              <el-option v-for="(model, index) in modelTemplates" :key="model.id"
                         :label="model.name" :value="model.name"></el-option>
              </el-select>
            </el-form-item>
             <el-form-item label="Metrics:" :prop="'models.'+index + '.metrics'">
              <el-select v-model="model.metrics" multiple placeholder="select metrics" style="width:100%">
               <el-option v-for="item in metrics" :key="item.name" :label="item.name" :value="item.name">
               </el-option>
              </el-select>
             </el-form-item>
             <el-form-item label="Config:" :prop="'models.' + index + '.config'">
               <el-input v-model="model.config" type="textarea" placeholder="{'model': {xxxxx}, 'metrics': {xxxxx}}">
               </el-input>
             </el-form-item>
           </div>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialog = false; clearJobForm()">Cancel</el-button>
          <el-button @click="resetForm('dialogData.jobForm')">Reset</el-button>
          <el-button @click="submitForm('dialogData.jobForm')">OK</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import ajax from '../request/index'
import myTable from '../components/JobTable'
// import router from '../router/index'

export default {
  components: {myTable},
  name: 'home',
  data() {
    return {
        jobCount: 0,
        tableData: {
           label: ['Job ID','Name', 'Status', 'Models', 'Create Time'],
           prop: ['id','name', 'status', 'models', 'start_time'],
           list: [],
          handleDetailClick: function (row) {
            if (row == null) {
              return
            }

            // router.push({ name: 'JobDetailView', params: { id: row.id }})
            window.location.href='detail?id='+row.id ;
          },

          handleStopClick: function (row) {
            if (row == null)  {
              return
            }
            // this.confirmStopJob(row);
             this.$confirm('This will stop this Job, continue?', 'Warning', {
              confirmButtonText: 'OK',
              cancelButtonText: 'Cancel',
              type: 'warning'
            }).then(() => {
              ajax.stopJobByID(row.id).then((result) => {
                if (result.data.code != 200) {
                this.$notify({
                  title: "ERROR",
                  type: 'error',
                  message: result.data.message,
                  duration: 0
                });
                return
              }
               this.$notify({
                  title: "SUCCESS",
                  type: 'success',
                  message: 'Start to stop!'
                });
              }).catch((resp) => {
                this.$notify({
                title: "ERROR",
                type: 'error',
                message: resp.message,
                duration: 0
                });
              });
              }).catch(() => {
                this.$notify({
                title: "INFO",
                type: 'info',
                message: 'Stop canceled'
              });
            });
          }.bind(this)
       },
       modelTemplates: [],
       metrics:[],
       dialog: false,
       dialogData: {
         title: '',
         jobForm: {
           name: '',
           data_source: '',
           timeout: '',
           models: []
         }
       }
     }
   },
  created() {
    ajax.getJobs().then((result) => {
      this.tableData.list = result.data.data;
      this.jobCount = this.tableData.list.length;
    }).catch(() => {});

    ajax.getModelTemplates().then((result) => {
      this.modelTemplates = result.data.data;
    }).catch(() => {});

    ajax.getMetrics().then((result) => {
      this.metrics = result.data.data;
    }).catch(() => {});
  },

  methods: {
    clickCreateJob: function () {
      this.dialogData.title = "Create New Job";
      this.dialogData.models = null;
      this.dialog = true;
    },

    addModel: function () {
        this.dialogData.jobForm.models.push({
          key: Date.now(),
          name: '',
        });
    },

    removeBox: function (item) {
       var index = this.dialogData.jobForm.models.indexOf(item)
       if (index !== -1) {
         this.dialogData.jobForm.models.splice(index, 1)
       }
     },

    clearJobForm: function () {
      this.dialogData.jobForm = {
        name: '',
        data_source: '',
        timeout: '',
        models: []
      }
    },

    resetForm: function (formName) {
        if (this.$refs[formName] != null) {
          this.$refs[formName].resetFields();
        }
    },

    submitForm: function (formName) {
      this.createJob()
    },

    createJob: function () {
      for (var i = 0; i < this.dialogData.jobForm.models.length; i++) {
        if (this.dialogData.jobForm.models[i].config != '' && this.dialogData.jobForm.models[i].config != null) {
          this.dialogData.jobForm.models[i].config = JSON.parse(this.dialogData.jobForm.models[i].config)
        }
      }
      ajax.setJob({
        "name": this.dialogData.jobForm.name,
        "timeout": this.dialogData.jobForm.timeout,
        "data_source": JSON.parse(this.dialogData.jobForm.data_source),
        "models": this.dialogData.jobForm.models
      }).then((result) => {
        if (result.data.code != 200) {
            this.$notify({
              title: "ERROR",
              type: 'error',
              message: result.data.message,
              duration: 0
            });
            return
          }
          this.dialog = false;
          this.tableData.list.unshift(result.data.data);
          this.jobCount = this.tableData.list.length;
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Create Job Success!'
          });
          this.clearJobForm();
      }).catch((resp) => {
        this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
      });
    },

    methods: {
      confirmStopJob: function (row) {
              },
    }
  }
}
</script>

<style>
  .me-models {
    margin-left: 1rem;
    margin-bottom: 1rem;
  }

  .me-a {
    margin-left: 1rem;
    color: blueviolet;
  }

</style>
