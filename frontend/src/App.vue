<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from './api'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const canOpenAdmin = ref(false)
const hasToken = computed(() => Boolean(localStorage.getItem('token')))
const isPublicPage = computed(() => ['login', 'register'].includes(route.name))

async function refreshAdminCapability() {
  if (!hasToken.value) {
    canOpenAdmin.value = false
    return
  }

  try {
    await api.get('/admin/users/pending')
    canOpenAdmin.value = true
  } catch {
    canOpenAdmin.value = false
  }
}

function logout() {
  auth.logout()
  canOpenAdmin.value = false
  router.push('/login')
}

onMounted(refreshAdminCapability)
watch(() => route.fullPath, refreshAdminCapability)
</script>

<template>
  <main class="app-shell">
    <header v-if="!isPublicPage" class="top-nav card">
      <div class="nav-title">宝宝记录</div>
      <nav class="nav-actions">
        <router-link class="nav-link" to="/record">记录</router-link>
        <router-link class="nav-link" to="/dashboard">主页</router-link>
        <router-link v-if="canOpenAdmin" class="nav-link" to="/admin">管理</router-link>
        <button class="ghost nav-logout" @click="logout">退出登录</button>
      </nav>
    </header>

    <router-view />
  </main>
</template>
