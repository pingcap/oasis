<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{scenesCount}}</span>
            </Strong>
          </div>
          <div>
            <el-button @click="clickCreateScenes()">New</el-button>
          </div>
        </div>
        <sh-table :tableData="tableData"></sh-table>
      </el-card>
    </div>
    <div>
      <div v-show="isShow" class="sch-detail">
        <el-collapse v-model="activeNames">
          <el-collapse-item title="Scenes Detail" name="1">
            <div class="sch-detail-header">
              <div class="sch-detail-summery">
                <span>Sence Name:
                  <strong> {{detail.name || ''}}</strong>
                </span>
              </div>
              <div>
                <!-- <el-button @click="clickDeleteScenes()">
                  <i class="fa fa-trash-o" aria-hidden="true"></i> Delete</el-button> -->
                <el-button @click="clickUpdateScenes()">
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
        <el-form :inline="true" :model="dialogData.scenesForm" ref="dialogData.scenesForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="dialogData.scenesForm.name"></el-input>
          </el-form-item>
          <el-form-item label="Creator:" prop="creator">
            <el-input v-model="dialogData.scenesForm.creator"></el-input>
          </el-form-item>
          <el-form-item label="Desc:" prop="desc">
            <el-input v-model="dialogData.scenesForm.desc"></el-input>
          </el-form-item>
          <div class="sch-boxes">
            <big>
              <strong>
                <span>Boxes: </span>
              </strong>
            </big>
            <a class="sch-a" @click="addBox">Add Box</a>
          </div>
          <div v-for="(box, index) in dialogData.scenesForm.boxes" :key="box.key">
            <div class="sch-boxes">
              <label>Box{{index}}</label>
              <a class="sch-a" @click="removeBox(box)"> Remove </a>
            </div>
            <el-form-item label="Name:" :prop="'boxes.' + index + '.name'">
              <el-input v-model="box.name"></el-input>
            </el-form-item>
            <el-form-item label="Cluster Template:" :prop="'boxes.'+index + '.cluster_template'">
              <el-select v-model="box.cluster_template" placeholder="select cluster template">
                <el-option v-for="(cluster, index) in clustersTemplate" :key="cluster.id" :label="cluster.name" :value="cluster.name"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="Cases Template:" :prop="'boxes.'+index + '.case_templates'">
              <el-select v-model="box.case_templates" multiple placeholder="select cases template" style="width: 33rem;">
                <el-option v-for="item in casesTemplate" :key="item.id" :label="item.name" :value="item.name">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="Lables:" :prop="'boxes.'+index + '.labels'"> 
               <el-input v-model="box.labels"></el-input>
            </el-form-item>
          </div>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialog = false; clearScenesForm()">Cancel</el-button>
          <el-button @click="resetForm('dialogData.scenesForm')">Reset</el-button>
          <el-button @click="submitForm('dialogData.scenesForm', dialogData.type)">OK</el-button>
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

    name: 'scenes',
    data() {
      return {
        activeNames: ['1'],
        isShow: false,
        detail: '',
        scenesCount: 0,
        clustersTemplate: [],
        casesTemplate: [],
        tableData: {
          label: ["Name", "Creator", "Update Time", "Boxes Count"],
          prop: ["name", "creator", "update_time", "boxes_count"],
          list: [],

          handleClick: function (row) {
            if (row == null) {
              return;
            }

            ajax.getScenesByName(row.name).then((result) => {
              this.detail = result.data.data;
              this.isShow = true;
            }).catch(() => {})
          }.bind(this)
        },

        dialog: false,
        dialogData: {
          title: '',
          scenesForm: {
            name: '',
            creator: '',
            desc: '',
            boxes: []
          }
        }
      }
    },

    created() {
      ajax.getScenes().then((result) => {
        result.data.data.forEach(function (element) {
          element.boxes_count = Object.keys(element.boxes).length;
        });
        this.tableData.list = result.data.data;
        this.scenesCount = this.tableData.list.length;
      }).catch(() => {})

      ajax.getClustersTemplate().then((result) => {
        this.clustersTemplate = result.data.data;
      }).catch(() => {})

      ajax.getCasesTemplate().then((result) => {
        this.casesTemplate = result.data.data;
      }).catch(() => {})
    },

    methods: {
      clickCreateScenes: function () {
        this.clearScenesForm();
        this.dialogData.title = "Create New Scenes";
        this.dialogData.type = "new";
        this.dialogData.boxes = null;
        this.dialog = true;
        return;
      },
      clickUpdateScenes: function () {
        var boxes = [];
        Object.values(this.detail.boxes).forEach(function (e) {
          // var cases = [];
          // Object.values(e.cases).forEach(function (c) {
          //   cases.push(c.name);
          // })

          var labelsToStr = function(labels) {
            var str = "";   
            var count = 0; 
            for(var key in labels) {
              if(count == 0) {
                  str += key+"="+labels[key]
              } else {
                  str += ","+key+"="+labels[key]
              }
              count++;
            }
            return str 
          }

          boxes.push({
            "name": e.name,
            "cluster_template": e.cluster_template,
            "case_templates": e.case_templates, 
            "labels": labelsToStr(e.labels)
          })
        })

        this.dialogData = Object.assign({}, this.dialogData, {
          title: "Update Scenes",
          type: "update",
          scenesForm: {
            name: this.detail.name,
            creator: this.detail.creator,
            desc: this.detail.desc,
            boxes: boxes
          }
        })

        this.dialog = true;
      },

      clickDeleteScenes: function () {
        this.$confirm('This will delete this Scenes, continue?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          ajax.deleteScenes(this.detail.name).then((result) => {
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
        return;
      },

      clearScenesForm: function () {
        this.dialogData.scenesForm = {
          name: '',
          creator: '',
          boxes: []
        }
      },

      resetForm: function (formName) {
        if (this.$refs[formName] != null) {
          this.$refs[formName].resetFields();
        }
      },

      addBox: function () {
        this.dialogData.scenesForm.boxes.push({
          key: Date.now(),
          name: '',
          cluster_template: '',
          case_templates: [],
          labels: ''
        });
      },

      removeBox: function (item) {
        var index = this.dialogData.scenesForm.boxes.indexOf(item)
        if (index !== -1) {
          this.dialogData.scenesForm.boxes.splice(index, 1)
        }
      },

      submitForm: function (formName, type) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            switch (type) {
              case "new":
                this.createScenes();
                break
              case "update":
                this.updateScenes();
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

      createScenes: function () {
        ajax.setScenes({
          name: this.dialogData.scenesForm.name,
          creator: this.dialogData.scenesForm.creator,
          desc: this.dialogData.scenesForm.desc,
          boxes: this.dialogData.scenesForm.boxes
        }).then((result) => {
          // console.log(result);
          //debugger;
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
          result.data.data.boxes_count = Object.keys(result.data.data.boxes).length;
          this.tableData.list.unshift(result.data.data);
          this.scenesCount = this.tableData.list.length;
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Create Scenes Success!'
          });
          this.clearScenesForm();
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },

      updateScenes: function () {
        ajax.setScenes({
          id: this.detail.id,
          name: this.dialogData.scenesForm.name,
          creator: this.dialogData.scenesForm.creator,
          desc: this.dialogData.scenesForm.desc,
          boxes: this.dialogData.scenesForm.boxes
        }).then((result) => {
          //      console.log(result.data);
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
            message: 'Update Scenes Success!'
          });

          ajax.getScenes().then((result) => {
            result.data.data.forEach(function (element) {
              element.boxes_count = Object.keys(element.boxes).length;
            });
            this.tableData.list = result.data.data;
            this.scenesCount = this.tableData.list.length;
          }).catch(() => {})
          this.isShow = false;
          this.clearScenesForm();
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

<style lang="scss">
  .sch-boxes {
    margin-left: 1rem;
    margin-bottom: 1rem;
  }

  .sch-a {
    margin-left: 1rem;
    color: blueviolet;
  }

</style>
