import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'

export default defineConfig({
  plugins: [
    frappeui({
      buildConfig: {
        outDir: '../mrvtools/public/frontend',
        baseUrl: '/assets/mrvtools/frontend/',
        indexHtmlPath: '../mrvtools/www/frontend.html',
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  optimizeDeps: {
    // frappe-ui's TextEditor imports virtual `~icons/lucide/*` modules that are
    // resolved by frappe-ui's own Rollup/Vite plugin. Pre-bundling runs esbuild,
    // which doesn't see Vite plugins — so we let dev serve frappe-ui through the
    // normal pipeline where the lucide resolver works.
    exclude: ['frappe-ui'],
    // ...but its CJS deps still need Vite's esbuild interop to synthesize a
    // `default` export. feather-icons is imported by frappe-ui's FeatherIcon.vue
    // as `import feather from 'feather-icons'`; without this include, the
    // pre-bundled module lacks a default and the page errors on load.
    include: ['feather-icons'],
  },
})
