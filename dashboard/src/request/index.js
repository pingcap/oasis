import Mock from 'mockjs'
import axios from 'axios'
const Proxy = '/api/v1'

class Ajax {
  getJobs() {
    return axios.get(`${Proxy}/jobs/list`)
  }
}
export default new Ajax()
