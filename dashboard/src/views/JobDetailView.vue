<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="job-search">
          <el-form >
            <el-input placeholder="Please input Job ID" v-model="jobID" class="input-with-select">
              <template slot="prepend">Job ID:</template>
              <el-button slot="append" @click="clickSearchJob">
                <i class="fa fa-search" aria-hidden="true"></i>
              </el-button>
            </el-input>
          </el-form>
        </div>
      </el-card>
    </div>
    <div v-show="isShow" class="sch-detail" v-if="jobDetail != ''" >
      <el-collapse  v-model="activeNames" >
        <el-collapse-item title="Job Detail" name="1">
          <div class="sch-detail-header">
            <div class="sch-detail-summery">
              <span>Job ID:
                <strong> {{jobDetail.id}}</strong>
              </span>
              <span>Status:
                <strong> {{jobDetail.status}}</strong>
              </span>
            </div>
          </div>
          <div class="sch-detail-body">
            <div class="me-detail">
              <el-tabs :tab-position="tabPosition" >
                <el-tab-pane label="Config">
                  <div class="me-pane">
                    <el-form ref="form" :label-position="labelPosition" label-width="10rem">
                      <el-form-item label="Start Time:">
                        <span>{{jobDetail.timeout}}</span>
                      </el-form-item>
                      <el-form-item label="Timeout:">
                        <span>{{jobDetail.timeout}}</span>
                      </el-form-item>
                      <el-form-item label="Slack Channel:">
                        <span>{{jobDetail.slack_channel}}</span>
                      </el-form-item>
                      <el-form-item label="Models:">
                        <span>{{jobDetail.models}}</span>
                      </el-form-item>
                      <el-form-item label="Data Source:">
                        <vue-json-pretty :data="JSON.parse(jobDetail.data_source)"></vue-json-pretty>
                      </el-form-item>
                      <el-form-item label="API Models Config:">
                        <vue-json-pretty :data="JSON.parse(jobDetail.api_models_config)"></vue-json-pretty>
                      </el-form-item>
                    </el-form>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="Models">
                  <div class="me-pane">
                    <!-- TODO: extract into separate componennts -->
                    <span v-for="model in jobDetail.model_instances">{{model.id}} - {{model.model}}</span>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    <div id="timeline-id"></div>
  </div>
</template>

<script>
  import ajax from '../request/index'
  import VueJsonPretty from 'vue-json-pretty'
import _ from 'lodash'
var DataSet = require('vis/lib/DataSet');
var Timeline = require('vis/lib/timeline/Timeline');

  export default {
    components: {
      VueJsonPretty
    },
    name: 'detail' ,
    data() {
      return {
        activeNames: ['1'],
        jobID: null,
        jobDetail: '',
        isShow: false,
        tabPosition: 'left',
        labelPosition: 'left'
      }
    },

    created() {
      var job_id = this.$route.query.id
      if(job_id == undefined) {
        return
      }
      this.jobID = job_id
      this.clickSearchJob()
    },

    mounted: function () {
      const self = this
      this.$nextTick(()=> {
        // Code that will run only after the
        // entire view has been rendered
          self.container = document.getElementById('timeline-id')
          if(self.timelineData) {
            const {items, groups} = self.timelineData
            new Timeline(self.container, items, groups, {});
          }
      })
    },

    methods: {
      clickSearchJob: function () {
        if(this.jobID == undefined || this.jobID == null || this.jobID == "") {
          this.$message({
              type: 'warning',
              message: "Job ID is required !!"
          });
          return;
        }

        ajax.getJobByID(this.jobID).then((result) => {
          var data = result.data
          if(data.code !== 200){
             this.$notify({
               title: "error",
               type: 'error',
               message: data.message,
               duration: 0
             });
             return;
          }
          this.isShow = true
          this.jobDetail = data.data


          // TODO: model_instances report should be json
          // TODO: report should be a specfific interface
          const models = this.jobDetail.model_instances
          models.forEach((i, idx)=>{
            models[idx].report = JSON.parse(models[idx].report)
          })

          var groups = _.keys(models[0].report.metrics_report).map(m=>{
            return {
              id: m,
              content: m
            }
          })
          var items = _.flatten(_.values(models[0].report.metrics_report)).map(i=>{
            return {
              group: i.metric,
              className: i.is_match ? 'green' : 'red',
              title: JSON.stringify(i.predict_data),
              start: new Date(i.time),
            }
          })

          this.timelineData = [items, groups]
          if(this.container) {
            new Timeline(this.container, items, groups, {});
          }

        }).catch((resp) => {
          this.$notify({
              title: "error",
              type: 'error',
              message: resp.message,
              duration: 0
          });
        })
      }
    }
  }
</script>

<style>
  .me-detail {
    margin-top: 1rem;
  }

  .job-search {
    margin-top: 1rem;
  }

  .me-pane {
    margin-top: 1rem;
    margin-left: 1rem;
  }

.vis-item.green {
  background-color: green;
}
.vis-item.red {
  background-color: red;
}
</style>
