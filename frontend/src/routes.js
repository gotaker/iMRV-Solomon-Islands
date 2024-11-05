// import { userResource } from '@/data/user'
const routes = [
  {
    path: "",
    redirect: () => {
      return { path: "/home" };
    }
  },
  {
    path: "/frontend",
    redirect: () => {
      return { path: "/home" };
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: {
      title: 'Home'
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
    name: 'Landing',
    path: '/landing',
    component: () => import('@/pages/Landing.vue'),
    meta: {
      title: 'Landing'
    }
  },
  {
    name: 'About',
    path: '/about',
    component: () => import('@/pages/About.vue'),
    meta: {
      title: 'Home'
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
      title: 'Home'
    }
  },
  {
    name: 'Reports',
    path: '/reports',
    component: () => import('@/pages/Reports.vue'),
    meta: {
      title: 'Home'
    }
  },
  {
    name: 'KnowledgeResource',
    path: '/knowledgeresource',
    component: () => import('@/pages/KnowledgeResource.vue'),
    meta: {
      title: 'Home'
    }
  },
];
