<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const loginForm = reactive({ username: '', password: '' })
const loading = ref(false)
const message = ref('')

async function onLogin() {
  message.value = ''
  loading.value = true
  try {
    await auth.login(loginForm)
    await router.push('/record')
  } catch (err) {
    message.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}

function toRegister() {
  router.push('/register')
}
</script>

<template>
  <section class="auth-shell">
    <article class="card stack auth-card">
      <h1 class="title">宝宝记录</h1>
      <p class="subtitle">记录宝宝每天的重要时刻</p>
      <input v-model="loginForm.username" placeholder="用户名" />
      <input v-model="loginForm.password" type="password" placeholder="密码" />
      <button :disabled="loading" @click="onLogin">登录</button>
      <button class="ghost" @click="toRegister">去注册</button>
      <p class="note">{{ message }}</p>
    </article>
  </section>
</template>
