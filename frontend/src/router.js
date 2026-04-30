import { createRouter, createWebHistory } from 'vue-router'

// Document titles follow the editorial format `iMRV — <Page>`. The
// beforeEach guard sets `document.title` from `meta.title`; keep this list
// authoritative — copy here is what the browser tab will show.
const routes = [
  {
    path: '',
    redirect: () => {
      return { path: '/home' }
    },
  },
  {
    path: '/frontend',
    redirect: () => {
      return { path: '/home' }
    },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: {
      title: 'iMRV — Home',
    },
  },
  {
    path: '/new',
    name: 'WhataNew',
    component: () => import('@/pages/WhatsNew.vue'),
    meta: {
      title: 'iMRV — Field Notes',
    },
  },
  {
    name: 'About',
    path: '/about',
    component: () => import('@/pages/About.vue'),
    meta: {
      title: 'iMRV — About',
    },
  },
  {
    name: 'Project',
    path: '/project',
    component: () => import('@/pages/Projects.vue'),
    meta: {
      title: 'iMRV — Programs',
    },
  },
  {
    name: 'Climate',
    path: '/climate-change-division',
    component: () => import('@/pages/ClimateChange.vue'),
    meta: {
      title: 'iMRV — Climate Change Division',
    },
  },
  {
    name: 'Reports',
    path: '/reports',
    component: () => import('@/pages/Reports.vue'),
    meta: {
      title: 'iMRV — National GHG Inventory',
    },
  },
  {
    name: 'Support',
    path: '/support',
    component: () => import('@/pages/Support.vue'),
    meta: {
      title: 'iMRV — Support Centre',
    },
  },
  {
    name: 'KnowledgeResource',
    path: '/knowledgeresource',
    component: () => import('@/pages/KnowledgeResource.vue'),
    meta: {
      title: 'iMRV — Knowledge Resources',
    },
  },
  {
    name: 'Privacy',
    path: '/privacy',
    component: () => import('@/pages/Privacy.vue'),
    meta: { title: 'iMRV — Privacy' },
  },
  {
    name: 'Accessibility',
    path: '/accessibility',
    component: () => import('@/pages/Accessibility.vue'),
    meta: { title: 'iMRV — Accessibility' },
  },
  {
    name: 'Source',
    path: '/source',
    component: () => import('@/pages/Source.vue'),
    meta: { title: 'iMRV — Source' },
  },
  {
    name: 'OpenData',
    path: '/open-data',
    component: () => import('@/pages/OpenData.vue'),
    meta: { title: 'iMRV — Open Data API' },
  },
  {
    name: 'Methodology',
    path: '/methodology',
    component: () => import('@/pages/Methodology.vue'),
    meta: { title: 'iMRV — Methodology' },
  },
  // Catch-all: unknown SPA routes silently rendered nothing (white screen)
  // because <router-view> had no fallback. Redirect to home instead.
  {
    path: '/:pathMatch(.*)*',
    redirect: { path: '/home' },
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,

  scrollBehavior(to, from, savedPosition) {
    document.getElementById('app').scrollIntoView({ behavior: 'smooth' })
  },
})

router.beforeEach((to, from) => {
  document.title = to.meta?.title ?? 'iMRV'
})

export default router
