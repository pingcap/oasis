import request from 'superagent'

const r = {
  get(url) {
    return request.get((process.env.SERVICE_URL||"") + url)
  }
}

export default r
