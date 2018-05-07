<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{missionCount}}</span>
            </Strong>
          </div>
          <div>
            <el-radio-group v-model="period">
              <el-radio-button label="daily"></el-radio-button>
              <el-radio-button label="weekly"></el-radio-button>
              <el-radio-button label="monthly"></el-radio-button>
              <el-radio-button label="yearly"></el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <sh-table :tableData="tableData"></sh-table>
      </el-card>
    </div>
    <div v-show="isShow" class="sch-detail">
      <el-collapse v-model="activeNames">
        <el-collapse-item title="Mission Detail" name="1">
          <div class="sch-detail-header">
            <div class="sch-detail-summery">
              <span>Mission Name:
                <strong> {{detail.name}}</strong>
              </span>
              <span>Status:
                <strong> {{detail.status}}</strong>
              </span>
            </div>
            <!-- <div>
              <el-button>
                <i class="fa fa-play" aria-hidden="true"></i> Run</el-button>
              <el-button v-on:click="confirmStopMission()">
                <i class="fa fa-stop" aria-hidden="true"></i> Stop</el-button>
              <el-button>
                <i class="fa fa-pencil-square-o" aria-hidden="true"></i> Edit</el-button>
            </div> -->
          </div>
          <div class="sch-detail-body">
            <pre>{{detail}}</pre>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

  </div>

</template>

<script>
  import shTable from '../components/table';
  import ajax from '../request/index';

  export default {
    components: {
      shTable
    },
    name: 'daily',

    data() {
      return {
        activeNames: ['1'],
        isShow: false,
        detail: '',
        missionCount: 0,
        period: "daily",
        tableData: {
          label: ['Mission ID', 'Mission Name', 'Status', 'Scenes', 'Update Time'],
          prop: ['id', 'name', 'status', 'scenes.name', 'update_time'],
          list: [],

          handleClick: function (row) {
            if (row == null) {
              return
            }

            ajax.getMissionReportByID(row.id).then((result) => {
              this.detail = result.data.data;
              this.detail.scenes_name = row.scenes.name;
              this.detail.status = row.status;
              this.detail.name = row.name;
            }).catch(() => {})

            ajax.getMissionDetailByID(row.id).then((result) => {
              this.detail.name = result.data.data.name;
              this.detail.pd_version = result.data.data.pd_version;
              this.detail.tidb_version = result.data.data.tidb_version;
              this.detail.tikv_version = result.data.data.tikv_version;
              this.detail.timeout = result.data.data.timeout;
              if (result.data.data.messager.callback == "") {
                this.detail.slack_channel = "#stability_tester"
              } else {
                this.detail.slack_channel = result.data.data.messager.callback;
              }
            }).catch(() => {})

            this.isShow = true;
          }.bind(this)
        },
      }
    },

    created() {
      ajax.getMissionByPeriod(this.period).then((result) => {
        this.tableData.list = result.data.data;
        this.missionCount = this.tableData.list.length;
      }).catch(() => {})
    },

    methods: {
      confirmStopMission: function () {
        this.$confirm('This will stop this mission, continue?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          ajax.stopMissionByID(this.detail.id).then((result) => {
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
      }
    },

    watch: {
      period: function (val) {
        ajax.getMissionByPeriod(val).then((result) => {
          this.tableData.list = result.data.data;
          this.missionCount = this.tableData.list.length;
          this.detail = '';
          this.isShow = false;
        }).catch(() => {})
      }
    }
  }

</script>
