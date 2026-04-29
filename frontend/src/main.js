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

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)

app.mount('#app')
