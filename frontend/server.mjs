/** Production static SPA server with API/media reverse proxy and optional TLS. */
import { createReadStream, existsSync, readFileSync, statSync } from 'node:fs'
import { createServer as createHttpServer, request as proxyRequest } from 'node:http'
import { createServer as createHttpsServer } from 'node:https'
import { extname, resolve, sep } from 'node:path'

const args = process.argv.slice(2)
const option = (name, fallback) => {
  const index = args.indexOf(name)
  return index >= 0 ? args[index + 1] : fallback
}
const host = option('--host', '127.0.0.1')
const port = Number(option('--port', '5173'))
const root = resolve('dist')
const mimeTypes = {
  '.css': 'text/css; charset=utf-8', '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.webp': 'image/webp', '.woff2': 'font/woff2',
}

if (!existsSync(resolve(root, 'index.html'))) {
  throw new Error('frontend/dist is missing; run npm run build before starting the server')
}

function proxy(req, res) {
  const upstream = proxyRequest({
    hostname: '127.0.0.1', port: 8011, method: req.method, path: req.url, headers: req.headers,
  }, (response) => {
    res.writeHead(response.statusCode ?? 502, response.headers)
    response.pipe(res)
  })
  upstream.on('error', () => {
    if (!res.headersSent) res.writeHead(502, { 'content-type': 'application/json' })
    res.end('{"detail":"API unavailable"}')
  })
  req.pipe(upstream)
}

function serve(req, res) {
  if (req.url?.startsWith('/api/') || req.url?.startsWith('/media/')) return proxy(req, res)
  let pathname
  try { pathname = decodeURIComponent(new URL(req.url ?? '/', 'http://localhost').pathname) }
  catch { res.writeHead(400); res.end('Bad request'); return }
  let file = resolve(root, `.${pathname}`)
  if (file !== root && !file.startsWith(`${root}${sep}`)) {
    res.writeHead(403); res.end('Forbidden'); return
  }
  if (!existsSync(file) || !statSync(file).isFile()) file = resolve(root, 'index.html')
  const extension = extname(file)
  const headers = {
    'content-type': mimeTypes[extension] ?? 'application/octet-stream',
    'cache-control': file.endsWith('index.html') ? 'no-cache' : pathname.startsWith('/assets/') ? 'public, max-age=31536000, immutable' : 'public, max-age=3600',
    'x-content-type-options': 'nosniff',
  }
  res.writeHead(200, headers)
  if (req.method === 'HEAD') res.end()
  else createReadStream(file).pipe(res)
}

const tlsKey = process.env.VAMOS_TLS_KEY
const tlsCert = process.env.VAMOS_TLS_CERT
const server = tlsKey && tlsCert
  ? createHttpsServer({ key: readFileSync(tlsKey), cert: readFileSync(tlsCert) }, serve)
  : createHttpServer(serve)
server.listen(port, host, () => process.stdout.write(`Vamos web listening on ${tlsKey ? 'https' : 'http'}://${host}:${port}\n`))
