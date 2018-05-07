const SERVICE_URL = process.env.SERVICE_URL

module.exports = {
  NODE_ENV: '"production"',
  SERVICE_URL: SERVICE_URL ? JSON.stringify(SERVICE_URL) : '"http://localhost:3000"'
}
