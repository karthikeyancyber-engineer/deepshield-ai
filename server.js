const { createServer } = require("https")
const { readFileSync } = require("fs")
const { createProxyServer } = require("http-proxy")
const next = require("next")

const dev = true
const hostname = "0.0.0.0"
const port = 3000
const BACKEND = "http://localhost:8000"

const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

const proxy = createProxyServer({ target: BACKEND, changeOrigin: true })
proxy.on("error", (err, req, res) => {
  if (res && typeof res.writeHead === "function") {
    res.writeHead(502, { "Content-Type": "application/json" })
    res.end(JSON.stringify({ detail: "Backend unreachable" }))
  }
})

const httpsOptions = {
  key: readFileSync("certs/key.pem"),
  cert: readFileSync("certs/cert.pem"),
}

app.prepare().then(() => {
  createServer(httpsOptions, (req, res) => {
    if (req.url.startsWith("/api/")) {
      req.url = req.url.replace("/api", "") || "/"
      return proxy.web(req, res)
    }
    handle(req, res)
  }).listen(port, hostname, () => {
    console.log(`> HTTPS Ready on https://${hostname}:${port}`)
  })
})
