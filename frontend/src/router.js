import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'

const routes = [
  {
    path:"",
    redirect:()=>{
     return{path:"/home"}    
    }
  },
  {
    path:"/frontend",
    redirect:()=>{
     return{path:"/home"}   
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: {
      title: 'MRV Tool'
    }
  },
  {
    path: '/new',
    name: 'WhataNew',
    component: () => import('@/pages/WhatsNew.vue'),
    meta: {
      title: "What's new"
    }
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
    meta: {
      title: 'Login'
    }
  },

  {
    name: 'About',
    path: '/about',
    component: () => import('@/pages/About.vue'),
    meta: {
      title: 'About MRV'
    }
  },
  // {
  //   name: 'AboutPage',
  //   path: '/aboutpage',
  //   component: () => import('@/pages/AboutPage.vue'),
  // },
  {
    name: 'Project',
    path: '/project',
    component: () => import('@/pages/Projects.vue'),
    meta: {
      title: 'MRV Project'
    }
  },
  {
    name: 'Climate',
    path: '/climate-change-division',
    component: () => import('@/pages/ClimateChange.vue'),
    meta: {
      title: 'Climate Change Division'
    }
  },
  {
    name: 'Reports',
    path: '/reports',
    component: () => import('@/pages/Reports.vue'),
    meta: {
      title: 'MRV Report'
    }
  },
  {
    name: 'Support',
    path: '/support',
    component: () => import('@/pages/Support.vue'),
    meta: {
      title: 'MRV Report'
    }
  },
  {
    name: 'KnowledgeResource',
    path: '/knowledgeresource',
    component: () => import('@/pages/KnowledgeResource.vue'),
    meta: {
      title: 'Knowledge Resource'
    }
  },
]





let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,

  scrollBehavior(to, from, savedPosition){
    document.getElementById('app').scrollIntoView({ behavior: 'smooth' });
    // return savedPosition || {top:0}
  }
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = true
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})


router.beforeEach((to, from) => {
  document.title = to.meta?.title ?? 'MRV Tool'
})

export default router
