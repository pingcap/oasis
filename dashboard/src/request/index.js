import Mock from 'mockjs'
import axios from 'axios'
const Proxy = '/api/v1'

class Ajax {
  getJobs(offset, size) {
    return axios.get(`${Proxy}/jobs/list?offset=${offset}&size=${size}`)
  }

  getJobByID(id) {
    return axios.get(`${Proxy}/job/${id}/detail`)
  }

  getModelTemplates() {
    return axios.get(`${Proxy}/model_templates/list`)
  }

  getMetrics() {
    return axios.get(`${Proxy}/metrics/list`)
  }

  setJob(data) {
    return axios.post(`${Proxy}/job/new`, data)
  }

  stopJobByID(id) {
    return axios.get(`${Proxy}/job/${id}/stop`)
  }
}

export default new Ajax()
