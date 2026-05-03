<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const message = ref('')

async function onRegister() {
  message.value = ''
  loading.value = true
  try {
    await api.post('/auth/register', form)
    message.value = '注册成功，请等待管理员审核。'
    form.username = ''
    form.password = ''
  } catch (err) {
    message.value = err.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}

function toLogin() {
  router.push('/login')
}
</script>

<template>
  <section class="auth-shell">
    <article class="card stack auth-card">
      <h1 class="title">创建账号</h1>
      <p class="subtitle">账号需要管理员审核通过后才可登录。</p>
      <input v-model="form.username" placeholder="用户名" />
      <input v-model="form.password" type="password" placeholder="密码" />
      <button class="secondary" :disabled="loading" @click="onRegister">注册</button>
      <button class="ghost" @click="toLogin">返回登录</button>
      <p class="note">{{ message }}</p>
    </article>
  </section>
</template>
