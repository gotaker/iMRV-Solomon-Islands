import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'

// https://vitejs.dev/config/
export default defineConfig({
  // Dev-only proxy: forward backend paths to the local Frappe bench.
  // changeOrigin rewrites the Host header to mrv.localhost so Frappe's
  // virtual-host routing resolves to the right site. Production serves
  // everything through Frappe directly, so this block has no effect there.
  server: {
    proxy: {
      '/api':       { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/method':    { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/assets':    { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/files':     { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/private':   { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/app':       { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/login':     { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/logout':    { target: 'http://mrv.localhost:8000', changeOrigin: true },
      '/socket.io': { target: 'http://mrv.localhost:9000', ws: true, changeOrigin: true },
    },
  },

  plugins: [frappeui(), vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
    emptyOutDir: true,
    target: 'es2015',
  },
  optimizeDeps: {
    include: ['frappe-ui > feather-icons', 'showdown', 'engine.io-client'],
  },
})
