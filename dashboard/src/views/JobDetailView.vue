<template>
<div>
  <div class="job-detail">
    <el-card class="job-search-box-card">
      <div class="job-search">
        <el-form>
          <el-input placeholder="Please input Job ID" v-model="jobID" class="input-with-select">
            <template slot="prepend">Job ID:</template>
            <el-button slot="append" @click="clickSearchJob">
              <i class="fa fa-search" aria-hidden="true"></i>
            </el-button>
          </el-input>
        </el-form>
      </div>
      <div class="job-detail-content" v-show="isShow" v-if="jobDetail != ''">
        <el-tabs v-model="activeName" type="card" @tab-click="handleTabClick">
          <el-tab-pane label="Config" name="first">
            <div class="me-pane">
              <!-- <el-card> -->
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
                  <el-form-item label="Models:" id="Models">
                    <span>{{jobDetail.models}}</span>
                  </el-form-item>
                  <el-form-item label="Data Source:">
                    <vue-json-pretty :data="JSON.parse(jobDetail.data_source)"></vue-json-pretty>
                  </el-form-item>
                  <el-form-item label="API Models Config:">
                    <vue-json-pretty :data="JSON.parse(jobDetail.api_models_config)"></vue-json-pretty>
                  </el-form-item>
                </el-form>
              <!-- </el-card> -->
            </div>
          </el-tab-pane>
          <el-tab-pane label="Models" name="second">
            <div id="show-model-report">
              <el-card>
                <div id="model-type">
                  <el-cascader :options="modelMetricList.options"
                    v-model="modelMetricList.value"
                    @change="handleMetricChange">
                  </el-cascader>
                </div>
                <!-- put timelien here -->
                <div id="timeline-id"></div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</div>
</template>

<script>
import ajax from '../request/index'
import VueJsonPretty from 'vue-json-pretty'
import myCascader from '../components/Cascader'
import _ from 'lodash'
var DataSet = require('vis/lib/DataSet');
var Timeline = require('vis/lib/timeline/Timeline');

var fetchTimer;
export default {
  components: {
    VueJsonPretty,
    myCascader
  },
  name: 'detail',
  data() {
    return {
      jobID: null,
      jobDetail: '',
      isShow: false,
      isClicked: false,
      labelPosition: 'left',
      activeName: 'first',
      radio: '1',
      modelMetricList: {
        value: [],
        options:[]
      }
    }
  },

  created() {
    var job_id = this.$route.query.id
    if (job_id == undefined) {
      return
    }
    this.jobID = job_id
  },

  mounted: function() {
    const self = this
    // Check routing to JobDetail directly or by clicking 'detail'.
    // debugger
    if(this.jobID != null) {
        // console.log("this.$route.name: " + this.$route.name)
        self.fetchResult()
    }
  },

  methods: {
    handleMetricChange(e) {
      console.log(this.modelMetricList.value)
      // get selected model
      const [m, m2] = this.modelMetricList.value
      var model = 0
      var self = this
      fetchTimer && clearInterval(fetchTimer)
      self.showTimeline(m, m2)
      fetchTimer = setInterval(()=>{
        self.showTimeline(m, m2)
      },6000)
    },

    handleTabClick: function(tab) {
      if(this.activeName == "second") {
        if(!this.container) {
          this.container = document.getElementById('timeline-id')
        }
      }
    },

    showTimeline(modelIdx=0, metricKey) {
      var self = this
      ajax.getJobByID(this.jobID).then(result=>{
        var {data} = result.data
        const models = data.model_instances
        models.forEach(i=>{
          i.report = JSON.parse(i.report)
        })
        // var groups = _.keys(models[modelIdx].report.metrics_report).map(m => {
        //       return {
        //         id: m,
        //         content: m
        //       }
        //     })

        // debugger
          // var allItems = _.flatten(_.values(models[modelIdx].report.metrics_report))
          var items = models[modelIdx].report.metrics_report[metricKey].map(i => {
            return {
              group: i.metric,
              className: i.is_match ? 'true' : 'false',
              title: JSON.stringify(i.predict_data),
              start: new Date(i.time),
            }
          })

          // self.timelineData = [items, groups]
          if (self.container) {
            if(!self.timelineInstance) {
              self.timelineInstance = new Timeline(self.container, items.slice(0, 200), {});
            } else {
              self.timelineInstance.setData({
                items: items.slice(0, 200),
              })
            }
          }
      })



    },

    clickSearchJob: function() {
      this.isClicked = true
      if (this.jobID == undefined || this.jobID == null || this.jobID == "") {
        this.$message({
          type: 'warning',
          message: "Job ID is required !!"
        });
        return;
      }
      this.fetchResult()
    },

    fetchResult: function () {
      ajax.getJobByID(this.jobID).then((result) => {
        var data = result.data
        if (data.code !== 200) {
          this.$notify({
            title: "error",
            type: 'error',
            message: data.message,
            duration: 0
          });
          return;
        }
        this.isShow = true
        // if(!this.container) {
        //   this.container = document.getElementById('timeline-id')
        // }
        this.jobDetail = data.data

        // prepare data for cascader options
        const models = this.jobDetail.model_instances
        this.modelMetricList.options =_.map(models, (i, idx)=>{
          const report = JSON.parse(i.report)
          const opt = {
            label: report.model_name,
            value: idx,
            children: _.keys(report.metrics_report).map((k, idxx)=>{
              return {label: k, value: k}
            })
          }
          return opt
        })
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

.vis-item.true {
  background-color: green;

}

.vis-item.false {
  background-color: red;
}
.job-detail-content {
  padding: 20px
}
</style>
