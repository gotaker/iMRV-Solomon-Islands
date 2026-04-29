import './index.css'
import { createApp } from 'vue'
import axios from 'axios'
import router from './router'
import App from './App.vue'
import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'

// Send the Frappe CSRF token on every axios call so SPA `/api/method/*` fetches
// keep working when the visitor is also logged into the desk. The token is
// injected by Frappe's web layer via the `<!-- csrf_token -->` placeholder in
// index.html — it ends up on `window.frappe.csrf_token` for authenticated
// sessions and is absent for guests (where allow_guest endpoints don't enforce
// CSRF anyway). See BUG-010 in the 2026-04-26 UI/UX sweep.
const csrf =
  (typeof window !== 'undefined' &&
    ((window.frappe && window.frappe.csrf_token) || window.csrf_token)) ||
  null
if (csrf) {
  axios.defaults.headers.common['X-Frappe-CSRF-Token'] = csrf
}

// Helper: parse the csrf_token cookie (Frappe sets it Set-Cookie on session creation)
function readCsrfCookie() {
  const m = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)
  return m ? decodeURIComponent(m[1]) : null
}

// Helper: refetch a fresh CSRF token. Probes the v16 endpoint first, falls
// back to a GET /  + cookie parse so we don't depend on a specific endpoint
// existing in older Frappe versions.
async function refreshCsrfToken() {
  try {
    const r = await axios.get('/api/method/frappe.sessions.get_csrf_token', {
      __csrfRetried: true,
    })
    const t = r.data?.message || r.data
    if (t && typeof t === 'string') return t
  } catch (_) {
    // fall through to GET / fallback
  }
  try {
    await axios.get('/', { __csrfRetried: true })
    return readCsrfCookie()
  } catch (_) {
    return null
  }
}

// Detect Frappe's CSRFTokenError envelope. Frappe v16 surfaces this as either
// exc_type or in _server_messages; we check both.
function isCsrfError(err) {
  if (err.response?.status !== 400) return false
  const data = err.response.data || {}
  if (data.exc_type === 'CSRFTokenError') return true
  const msgs = data._server_messages
  if (typeof msgs === 'string' && msgs.includes('CSRFTokenError')) return true
  return false
}

axios.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (!isCsrfError(err)) return Promise.reject(err)
    const cfg = err.config || {}
    if (cfg.__csrfRetried) return Promise.reject(err)
    const token = await refreshCsrfToken()
    if (!token) return Promise.reject(err)
    axios.defaults.headers.common['X-Frappe-CSRF-Token'] = token
    if (typeof window !== 'undefined' && window.frappe) {
      window.frappe.csrf_token = token
    }
    cfg.headers = cfg.headers || {}
    cfg.headers['X-Frappe-CSRF-Token'] = token
    cfg.__csrfRetried = true
    console.warn('[csrf] stale token; refreshed and retrying')
    return axios(cfg)
  },
)

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)

app.mount('#app')
