import { createRouter, createWebHashHistory } from 'vue-router'

import AdminView from './views/AdminView.vue'
import DashboardView from './views/DashboardView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import RecordView from './views/RecordView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/record' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/record', name: 'record', component: RecordView },
    { path: '/admin', name: 'admin', component: AdminView }
  ]
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const publicPages = ['login', 'register']
  if (!publicPages.includes(to.name) && !token) {
    return { name: 'login' }
  }
  if (publicPages.includes(to.name) && token) {
    return { name: 'record' }
  }
  return true
})

export default router
