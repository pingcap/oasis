<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{clusterCount}}</span>
            </Strong>
          </div>
          <div>
            <el-button @click="clickCreateClusterTemplate()">New</el-button>
          </div>
        </div>
        <sh-table :tableData="tableData"></sh-table>
      </el-card>
    </div>
    <div>
      <div v-show="isShow" class="sch-detail">
        <el-collapse v-model="activeNames">
          <el-collapse-item title="Case Template Detail" name="1">
            <div class="sch-detail-header">
              <div class="sch-detail-summery">
                <span>Cluster Template:
                  <strong> {{detail.name || ''}}</strong>
                </span>
              </div>
              <div>
                <!-- <el-button @click="clickDeleteClusterTemplate()">
                  <i class="fa fa-trash-o" aria-hidden="true"></i> Delete</el-button> -->
                <el-button @click="clickUpdateClusterTemplate()">
                  <i class="fa fa-pencil-square-o" aria-hidden="true"></i> Edit</el-button>
              </div>
            </div>
            <div class="sch-detail-body">
              <pre>{{detail}}</pre>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    <div>
      <el-dialog :title="dialogData.title" :visible.sync="dialog">
        <el-form :inline="true" :model="dialogData.clusterForm" :rules="dialogData.clusterRules" ref="dialogData.clusterForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="dialogData.clusterForm.name"></el-input>
          </el-form-item>
          <el-form-item label="Creator:" prop="creator">
            <el-input v-model="dialogData.clusterForm.creator"></el-input>
          </el-form-item>
          <el-form-item label="PD Size:" prop="pd">
            <el-input v-model.number="dialogData.clusterForm.pd" auto-complete="off"></el-input>
          </el-form-item>
          <el-form-item label="TiDB Size:" prop="tidb">
            <el-input v-model.number="dialogData.clusterForm.tidb" auto-complete="off"></el-input>
          </el-form-item>
          <el-form-item label="TiKV Size:" prop="tikv">
            <el-input v-model.number="dialogData.clusterForm.tikv" auto-complete="off"></el-input>
          </el-form-item>
          <el-form-item label="ConfigMap:" prop="config_map">
            <el-input v-model="dialogData.clusterForm.config_map"></el-input>
          </el-form-item>
          <el-form-item label="Description:" prop="desc">
            <el-input v-model="dialogData.clusterForm.desc"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialog = false; clearClusterForm()">Cancel</el-button>
          <el-button @click="resetForm('dialogData.clusterForm')">Reset</el-button>
          <el-button @click="submitForm('dialogData.clusterForm', dialogData.type)">OK</el-button>
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

    name: 'cluster',

    data() {
      return {
        activeNames: ['1'],
        isShow: false,
        detail: '',
        clusterCount: 0,
        tableData: {
          label: ["Name", "Creator", "PD Size", "TiDB Size", "TiKV Size", "ConfigMap", "Description"],
          prop: ["name", "creator", "pd", "tidb", "tikv", "config_map"],
          list: [],

          handleClick: function (row) {
            if (row == null) {
              return;
            }
            ajax.getClusterTemplateByName(row.name).then((result) => {
              this.detail = result.data.data;
              this.isShow = true;
            }).catch(() => {})
          }.bind(this)
        },
        dialog: false,
        dialogData: {
          title: '',
          clusterForm: {
            name: '',
            creator: '',
            pd: 3,
            tidb: 3,
            tikv: 5,
            config_map: '',
            desc: ''
          },

          type: '',

          clusterRules: {
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
            creator: [{
                required: true,
                message: 'Please input creator',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ],
            pd: [{
                required: true,
                message: 'Please input pd size',
              },
              {
                type: 'number',
                message: 'must number'
              }
            ],
            tidb: [{
                required: true,
                message: 'Please input tidb size',
              },
              {
                type: 'number',
                message: 'must number'
              }
            ],
            tikv: [{
                required: true,
                message: 'Please input tikv size',
              },
              {
                type: 'number',
                message: 'must number'
              }
            ],
            config_map: [{
                required: true,
                message: 'Please input config_map',
                trigger: 'blur'
              },
              {
                min: 1,
                max: 64,
                message: 'Length should be 1 to 64',
                trigger: 'blur'
              }
            ]
          }
        }
      }
    },

    created() {
      ajax.getClustersTemplate().then((result) => {
        this.tableData.list = result.data.data;
        this.clusterCount = this.tableData.list.length;
      }).catch(() => {})
    },

    methods: {
      clickCreateClusterTemplate: function () {
        // this.clearClusterForm();
        this.dialogData.title = "Create Cluster Template";
        this.dialogData.type = "new";
        this.dialog = true;
      },

      clickDeleteClusterTemplate: function () {
        this.$confirm('This will delete this cluster template, continue?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          ajax.deleteClusterTemplate(this.detail.name).then((result) => {
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
              message: 'Delete success!'
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
            message: 'Delete canceled'
          });
        });
      },

      clickUpdateClusterTemplate: function () {
        this.dialogData = Object.assign({}, this.dialogData, {
          title: "Update Cluster Template",
          type: "update",
          clusterForm: this.detail
        })
        this.dialog = true;
      },

      clearClusterForm: function () {
        this.dialogData.clusterForm = {
          name: '',
          creator: '',
          pd: 3,
          tidb: 3,
          tikv: 5,
          config_map: '',
          desc: ''
        }
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
                this.createClusterTemplate()
                break
              case "update":
                this.updateClusterTemplate()
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

      createClusterTemplate: function () {
        ajax.setClusterTemplate({
          name: this.dialogData.clusterForm.name,
          creator: this.dialogData.clusterForm.creator,
          pd: this.dialogData.clusterForm.pd,
          tidb: this.dialogData.clusterForm.tidb,
          tikv: this.dialogData.clusterForm.tikv,
          config_map: this.dialogData.clusterForm.config_map,
          desc: this.dialogData.clusterForm.desc
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
          this.clusterCount = this.tableData.list.length;
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Create Cluster Template Success!'
          });
          this.clearClusterForm();
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },

      updateClusterTemplate: function () {
        ajax.setClusterTemplate({
          id: this.detail.id,
          name: this.dialogData.clusterForm.name,
          creator: this.dialogData.clusterForm.creator,
          pd: this.dialogData.clusterForm.pd,
          tidb: this.dialogData.clusterForm.tidb,
          tikv: this.dialogData.clusterForm.tikv,
          config_map: this.dialogData.clusterForm.config_map,
          desc: this.dialogData.clusterForm.desc
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
          //this.tableData.list.unshift(result.data);
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Update Cluster Template Success!'
          });
          ajax.getClustersTemplate().then((result) => {
            this.tableData.list = result.data.data;
            this.clusterCount = this.tableData.list.length;
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
