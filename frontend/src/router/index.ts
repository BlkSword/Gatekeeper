import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

import HomeView from '../views/HomeView.vue'
import CheckView from '../views/CheckView.vue'
import SettingsView from '../views/SettingsView.vue'
import LoginView from '../views/LoginView.vue'

import AccountSettings from '../views/Setting/AccountSettings.vue'
import PasswordSettings from '../views/Setting/PasswordSettings.vue'
import AlertSettings from '../views/Setting/AlertSettings.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/check',
    name: 'Check',
    component: CheckView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true },
    redirect: '/settings/account',
    children: [
      {
        path: 'account',
        name: 'AccountSettings',
        component: AccountSettings
      },
      {
        path: 'password',
        name: 'PasswordSettings',
        component: PasswordSettings
      },
      {
        path: 'alert',
        name: 'AlertSettings',
        component: AlertSettings
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth) {
    if (!authStore.token) {
      next({ path: '/login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router