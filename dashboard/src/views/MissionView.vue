<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <!-- <div class="sch-search">
          <el-input placeholder="Please input " v-model="searchName" class="input-with-select">
            <template slot="prepend">Mission Name: </template>
            <el-button slot="append" @click="searchMission">
              <i class="fa fa-search" aria-hidden="true"></i>
            </el-button>
          </el-input>
        </div> -->
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{missionCount}}</span>
            </Strong>
          </div>
          <div>
            <el-button @click="clickCreateMission">New</el-button>
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
            <div>
              <el-button @click="clickRunMission">
                <i class="fa fa-play" aria-hidden="true"></i> Run</el-button>
              <el-button v-on:click="confirmStopMission()">
                <i class="fa fa-stop" aria-hidden="true"></i> Stop</el-button>
              <el-button @click="clickUpdateMission">
                <i class="fa fa-pencil-square-o" aria-hidden="true" @click="clickUpdateMission"></i> Edit</el-button>
            </div>
          </div>
          <div class="sch-detail-body">
            <pre>{{detail}}</pre>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    <div>
      <el-dialog :title="dialogData.title" :visible.sync="dialog">
        <el-form :inline="true" :model="dialogData.missionForm" :rules="dialogData.missionRules" ref="dialogData.missionForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="dialogData.missionForm.name"></el-input>
          </el-form-item>
          <el-form-item label="Scenes:" prop="scenes_name">
            <el-select v-model="dialogData.missionForm.scenes_name" placeholder="select scenes">
              <el-option v-for="(s, index) in scenes" :key="s.id" :label="s.name" :value="s.name"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="PD Version:" prop="pd_version">
            <el-input v-model="dialogData.missionForm.pd_version"></el-input>
          </el-form-item>
          <el-form-item label="TiDB Version:" prop="tidb_version">
            <el-input v-model="dialogData.missionForm.tidb_version"></el-input>
          </el-form-item>
          <el-form-item label="TiKV Version:" prop="tikv_version">
            <el-input v-model="dialogData.missionForm.tikv_version"></el-input>
          </el-form-item>
          <el-form-item label="Slack Channel:" prop="slack_channel">
            <el-input v-model="dialogData.missionForm.slack_channel"></el-input>
          </el-form-item>
          <el-form-item label="Timeout:" prop="timeout">
            <el-input v-model="dialogData.missionForm.timeout"></el-input>
          </el-form-item>
          <el-form-item label="IgnoreErrors:" prop="ignore_errors">
            <el-input v-model="dialogData.missionForm.ignore_errors"></el-input>
          </el-form-item>
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
  import shTable from '../components/table';
  import ajax from '../request/index'

  export default {
    components: {
      shTable
    },

    name: "mission",

    data() {
      return {
        missionCount: 0,
        activeNames: ['1'],
        isShow: false,
        detail: '',
        scenes: [],
        tableData: {
          label: ['Mission ID', 'Mission Name', 'Status', 'Scenes', 'Update Time','Slack Channel'],
          prop: ['id', 'name', 'status', 'scenes.name', 'update_time', 'messager.callback'],
          list: [],

          handleClick: function (row) {
            if (row == null) {
              return
            }

            ajax.getMissionReportByID(row.id).then((result) => {
              this.detail = result.data.data;
              this.detail.scenes_name = row.scenes.name;
              this.detail.status = row.status;
              this.detail.slack_channel = row.messager.callback;
              this.detail.id = row.id;
            }).catch(() => {})

            ajax.getMissionDetailByID(row.id).then((result) => {
              this.detail.name = result.data.data.name;
              this.detail.pd_version = result.data.data.pd_version;
              this.detail.tidb_version = result.data.data.tidb_version;
              this.detail.tikv_version = result.data.data.tikv_version;
              this.detail.timeout = result.data.data.timeout;
              this.detail.ignore_errors = result.data.data.ignore_errors;
              if (result.data.data.messager.callback == "") {
                this.detail.slack_channel = "#stability_tester"
              } else {
                this.detail.slack_channel = result.data.data.messager.callback;
              }
            }).catch(() => {})

            this.isShow = true;
          }.bind(this)
        },

        dialog: false,
        dialogData: {
          title: '',
          missionForm: {
            name: '',
            scenes_name: '',
            pd_version: '',
            tidb_version: '',
            tikv_version: '',
            slack_channel: '',
            timeout: '',
            ignore_errors: '',
          },
          type: '',
          missionRules: {
            name: [{
                required: true,
                message: 'Please input name',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ],
            scenes_name: [{
              required: true,
              message: 'Please select scenes',
              trigger: 'chanege'
            }],
            pd_version: [{
                required: true,
                message: 'Please pd version',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 200,
                message: 'Length should be 1 to 200',
                trigger: 'blur'
              }
            ],
            tikv_version: [{
                required: true,
                message: 'Please tikv version',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 200,
                message: 'Length should be 1 to 200',
                trigger: 'blur'
              }
            ],
            tidb_version: [{
                required: true,
                message: 'Please tidb version',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 200,
                message: 'Length should be 1 to 200',
                trigger: 'blur'
              }
            ],
            slack_channel: [{
                required: true,
                message: 'Please input name',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ],
            timeout: [{
                required: true,
                message: 'Please input name',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ],
            ignore_errors: [{
                required: false,
                message: 'Please input ignore error',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ],
          }
        }

      }
    },

    created() {
      ajax.getMissions().then((result) => {
        this.tableData.list = result.data.data;
        this.missionCount = this.tableData.list.length;
      }).catch(() => {})

      ajax.getScenes().then((result) => {
        this.scenes = result.data.data;
      }).catch(() => {})
    },

    methods: {
      clickCreateMission: function () {
        this.dialogData = Object.assign({}, this.dialogData, {
          title: "Create New Mission",
          type: "new",
        })
        this.dialog = true;
      },

      clickUpdateMission: function () {
        this.dialogData = Object.assign({}, this.dialogData, {
          title: "Update Mission",
          type: "update",
          missionForm: this.detail
        })

        this.dialog = true;
      },

      clickRunMission: function () {
        ajax.updateMission(this.detail).then((result) => {
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
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Start Mission Success!'
          });

          ajax.getMissions().then((result) => {
            this.tableData.list = result.data.data;
            this.missionCount = this.tableData.list.length;
          }).catch(() => {})
          this.isShow = false;
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },

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
      },

      resetForm(formName) {
        if (this.$refs[formName] != null) {
          this.$refs[formName].resetFields();
        }
      },

      submitForm: function (formName, type) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            switch (type) {
              case "new":
                this.createMission();
                break
              case "update":
                this.updateMission();
                break
              default:
                alert("Error");
                break;
            }
          } else {
            console.log('error submit!!');
            return false;
          }
        });
      },

      clearMissionForm: function () {
        this.dialogData.missionForm = {
          name: '',
          scenes_name: '',
          pd_version: '',
          tidb_version: '',
          tikv_version: '',
          slack_channel: '#stability_tester',
          timeout: ''
        }
      },

      createMission: function () {
        ajax.startMission(
          //     {
          //     name: this.dialogData.missionForm.name,
          //     scenes: this.dialogData.missionForm.scenes,
          //     pd_version: this.dialogData.missionForm.pd_version,
          //     tidb_version: this.dialogData.missionForm.tidb_version,
          //     tikv_version: this.dialogData.missionForm.tikv_version,
          //     slack_channel: this.dialogData.missionForm.slack_channel,
          //     timeout: this.dialogData.missionForm.timeout
          // }
          this.dialogData.missionForm
        ).then((result) => {
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
          this.missionCount = this.tableData.list.length;
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Create Mission Success!'
          });
          this.clearMissionForm();
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },

      updateMission: function () {
        ajax.updateMission(this.dialogData.missionForm).then((result) => {
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
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Update Mission Success!'
          });
          ajax.getMissions().then((result) => {
            this.tableData.list = result.data.data;
            this.missionCount = this.tableData.list.length;
          }).catch(() => {})
          this.isShow = false;
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
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
  .el-select .el-input {
    width: 10rem;
  }


  .input-with-select .el-input-group__prepend {
    background-color: #fff;
  }

  .el-input-group {
    margin-bottom: 1rem;
  }

  .sch-search {
    margin-top: 1rem;
  }

</style>
