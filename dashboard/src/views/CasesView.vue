<template>
  <div>
    <div class="card">
      <el-card class="box-card">
        <div class="sch-card-header">
          <div>
            <Strong>
              <span>Count: {{caseCount}}</span>
            </Strong>
          </div>
          <div>
            <el-button @click="clickCreateCaseTemplate()">New</el-button>
          </div>
        </div>
        <sh-table :tableData="tableData"></sh-table>
      </el-card>
    </div>
    <div v-show="isShow" class="sch-detail">
      <el-collapse v-model="activeNames">
        <el-collapse-item title="Case Template Detail" name="1">
          <div class="sch-detail-header">
            <div class="sch-detail-summery">
              <span>Case Name:
                <strong> {{detail.name || ''}}</strong>
              </span>
              <span>Type:
                <strong> {{detail.type}}</strong>
              </span>
            </div>
            <div>
              <!-- <el-button @click="clickDeleteCaseTemplate()">
                <i class="fa fa-trash-o" aria-hidden="true"></i> Delete</el-button> -->
              <el-button @click="clickUpdateCaseTemplate()">
                <i class="fa fa-pencil-square-o" aria-hidden="true"></i> Edit</el-button>
            </div>
          </div>
          <div class="sch-detail-body">
            <pre>
                  {{detail}}
              </pre>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    <div>
      <el-dialog title="Create Case Template" :visible.sync="dialogCreateCaseTemplate">
        <el-form :inline="true" :model="caseForm" :rules="rules" ref="caseForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="caseForm.name"></el-input>
          </el-form-item>
          <el-form-item label="Type:" prop="type">
            <el-select v-model="caseForm.type" placeholder="select type">
              <el-option label="test case" value="test case"></el-option>
              <el-option label="auxiliary tool" value="auxiliary tool"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Creator:" prop="creator">
            <el-input v-model="caseForm.creator"></el-input>
          </el-form-item>
          <el-form-item label="Description:" prop="desc">
            <el-input v-model="caseForm.desc"></el-input>
          </el-form-item>
          <div class="sch-source">
            <big>
              <strong>
                <span>Source: </span>
              </strong>
            </big>
          </div>
          <el-form-item label="Binary Name:" prop="binary_name">
            <el-input v-model="caseForm.binary_name"></el-input>
          </el-form-item>
          <el-form-item label="Source Type:" prop="source_type">
            <el-select v-model="caseForm.source_type" placeholder="select source type">
              <el-option label="git" value="git"></el-option>
              <el-option label="bin" value="bin"></el-option>
              <!-- <el-option label="docker" value="docker"></el-option> -->
            </el-select>
          </el-form-item>
          <el-form-item label="Git Repo:" prop="git_repo">
            <el-input v-model="caseForm.git_repo"></el-input>
          </el-form-item>
          <el-form-item label="Git Value:" prop="git_value">
            <el-input v-model="caseForm.git_value"></el-input>
          </el-form-item>
          <el-form-item label="Binary URL:" prop="source_url">
            <el-input v-model="caseForm.source_url"></el-input>
          </el-form-item>
          <el-form-item label="Args:" prop="args">
            <el-input v-model="caseForm.args"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogCreateCaseTemplate = false; clearCaseForm()">Cancel</el-button>
          <el-button @click="resetForm('caseForm')">Reset</el-button>
          <el-button @click="submitForm('caseForm', 'new')">OK</el-button>
        </div>
      </el-dialog>

      <el-dialog title="Update Case Template" :visible.sync="dialogUpdateCaseTemplate">
        <el-form :inline="true" :model="caseForm" :rules="rules" ref="caseForm" label-width="6rem">
          <el-form-item label="Name:" prop="name">
            <el-input v-model="caseForm.name"></el-input>
          </el-form-item>
          <el-form-item label="Type:" prop="type">
            <el-select v-model="caseForm.type" placeholder="select type">
              <el-option label="test case" value="test case"></el-option>
              <el-option label="auxiliary tool" value="auxiliary tool"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Creator:" prop="creator">
            <el-input v-model="caseForm.creator"></el-input>
          </el-form-item>
          <el-form-item label="Description:" prop="desc">
            <el-input v-model="caseForm.desc"></el-input>
          </el-form-item>
          <div class="sch-source">
            <big>
              <strong>
                <span>Source: </span>
              </strong>
            </big>
          </div>
          <el-form-item label="Binary Name:" prop="binary_name">
            <el-input v-model="caseForm.binary_name"></el-input>
          </el-form-item>
          <el-form-item label="Source Type:" prop="source_type">
            <el-select v-model="caseForm.source_type" placeholder="select source type">
              <el-option label="git" value="git"></el-option>
              <el-option label="bin" value="bin"></el-option>
              <!-- <el-option label="docker" value="docker"></el-option> -->
            </el-select>
          </el-form-item>
          <el-form-item label="Git Repo:" prop="git_repo">
            <el-input v-model="caseForm.git_repo"></el-input>
          </el-form-item>
          <el-form-item label="Git Value:" prop="git_value">
            <el-input v-model="caseForm.git_value"></el-input>
          </el-form-item>
          <el-form-item label="Binary URL:" prop="source_url">
            <el-input v-model="caseForm.source_url"></el-input>
          </el-form-item>
          <el-form-item label="Arg:" prop="args">
            <el-input v-model="caseForm.args"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogUpdateCaseTemplate = false; clearCaseForm()">Cancel</el-button>
          <el-button @click="resetForm('caseForm')">Reset</el-button>
          <el-button @click="submitForm('caseForm','update')">Save</el-button>
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

    name: 'cases',

    data() {
      return {
        activeNames: ['1'],
        isShow: false,
        detail: '',
        lastDetail: '',
        caseCount: 0,
        tableData: {
          label: ["Name", "Creator", "Update Time", "Type"],
          prop: ["name", "creator", "update_time", "type"],
          list: [],

          handleClick: function (row) {
            if (row == null) {
              return;
            }
            ajax.getCaseTemplateByName(row.name).then((result) => {
              this.detail = result.data.data;
              this.isShow = true;
              this.lastDetail = row;
            }).catch(() => {})
          }.bind(this)
        },

        dialogCreateCaseTemplate: false,
        dialogUpdateCaseTemplate: false,
        caseForm: {
          name: '',
          creator: '',
          type: '',
          desc: '',
          binary_name: '',
          source_type: '',
          source_url: '',
          git_repo: '',
          git_value: '',
          args: ''
        },

        rules: {
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
          type: [{
            required: true,
            message: 'Please select type',
            trigger: 'change'
          }],
          desc: [{
            required: true,
            message: 'Please input description',
            trigger: 'blur'
          }],
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
          binary_name: [{
              required: true,
              message: 'Please input binary name',
              trigger: 'blur'
            },
            {
              min: 1,
              max: 64,
              message: 'Length should be 1 to 64',
              trigger: 'blur'
            }
          ],
          source_type: [{
            required: true,
            message: 'Please select source type',
            trigger: 'change'
          }]
        }
      }
    },

    created() {
      ajax.getCasesTemplate().then((result) => {
        this.tableData.list = result.data.data;
        this.caseCount = this.tableData.list.length;
      }).catch(() => {})
    },

    methods: {
      createCaseTemplate: function () {
        ajax.createCaseTemplate({
          name: this.caseForm.name,
          creator: this.caseForm.creator,
          type: this.caseForm.type,
          desc: this.caseForm.desc,
          args: this.caseForm.args,
          source: {
            binary_name: this.caseForm.binary_name,
            type: this.caseForm.source_type,
            git_repo: this.caseForm.git_repo,
            git_value: this.caseForm.git_value,
            url: this.caseForm.source_url
          }
        }).then((result) => {
          console.log(result);
          if (result.data.code != 200) {
            this.$notify({
              title: "ERROR",
              type: 'error',
              message: result.data.message,
              duration: 0
            });
            return
          }

          this.dialogCreateCaseTemplate = false;
          this.tableData.list.unshift(result.data.data);
          this.caseCount = this.tableData.list.length;
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Create Case Template Success!'
          });
          this.clearCaseForm()
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },

      updateCaseTemplate: function () {
        ajax.updateCaseTemplate({
          id: this.detail.id,
          name: this.caseForm.name,
          creator: this.caseForm.creator,
          create_time: this.detail.create_time,
          type: this.caseForm.type,
          desc: this.caseForm.desc,
          args: this.caseForm.args,
          source: {
            binary_name: this.caseForm.binary_name,
            type: this.caseForm.source_type,
            git_repo: this.caseForm.git_repo,
            git_value: this.caseForm.git_value,
            url: this.caseForm.source_url
          }
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

          this.dialogUpdateCaseTemplate = false;
          //this.tableData.list.unshift(result.data);
          this.$notify({
            title: "SUCCESS",
            type: 'success',
            message: 'Update Case Template Success!'
          });
          ajax.getCasesTemplate().then((result) => {
            this.tableData.list = result.data.data;
            this.caseCount = this.tableData.list.length;
          }).catch(() => {})
          this.isShow = false;
          this.clearCaseForm();
        }).catch((resp) => {
          this.$notify({
            title: "ERROR",
            type: 'error',
            message: resp.message,
            duration: 0
          });
        })
      },


      submitForm: function (formName, type) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            switch (type) {
              case "new":
                this.createCaseTemplate()
                break
              case "update":
                this.updateCaseTemplate()
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

      resetForm(formName) {
        if (this.$refs[formName] != null) {
          this.$refs[formName].resetFields();
        }
      },

      clickDeleteCaseTemplate: function () {
        this.$confirm('This will delete this case template, continue?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          ajax.deleteCaseTemplate(this.detail.name).then((result) => {
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

      clickUpdateCaseTemplate: function () {
        // this.clearCaseForm();
        this.caseForm = {
          name: this.detail.name,
          creator: this.detail.creator,
          type: this.detail.type,
          desc: this.detail.desc,
          binary_name: this.detail.source.binary_name,
          source_type: this.detail.source.type,
          git_repo: this.detail.source.git_repo,
          git_value: this.detail.source.git_value,
          args: this.detail.args,
          source_url: this.detail.source.url
        };
        this.dialogUpdateCaseTemplate = true;
      },

      clickCreateCaseTemplate: function () {
        this.clearCaseForm();
        this.resetForm('caseForm');
        this.dialogCreateCaseTemplate = true;
      },

      clearCaseForm: function () {
        this.caseForm = {
          name: '',
          creator: '',
          type: '',
          desc: '',
          binary_name: '',
          source_type: '',
          git_repo: '',
          git_value: '',
          args: '',
          source_url: ''
        }
      }
    }
  }

</script>
<style lang="scss">
  .sch-source {
    margin-left: 1rem;
    margin-bottom: 1rem;
  }

</style>
