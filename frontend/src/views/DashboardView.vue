<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const babies = ref([])
const newBaby = ref({ name: '', birth_date: '' })
const message = ref('')
const canOpenAdmin = ref(false)

async function loadBabies() {
  const { data } = await api.get('/babies')
  babies.value = data
}

async function loadAdminCapability() {
  try {
    await api.get('/admin/users/pending')
    canOpenAdmin.value = true
  } catch {
    canOpenAdmin.value = false
  }
}

async function createBaby() {
  message.value = ''
  try {
    await api.post('/babies', newBaby.value)
    newBaby.value = { name: '', birth_date: '' }
    await loadBabies()
  } catch (err) {
    message.value = err.response?.data?.detail || '新增宝宝失败'
  }
}

function toAdmin() {
  router.push('/admin')
}

function toRecord() {
  router.push('/record')
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  await Promise.all([loadBabies(), loadAdminCapability()])
})
</script>

<template>
  <section class="stack">
    <article class="card stack">
      <div class="grid grid-2">
        <h1 class="title">你好，{{ auth.username }}</h1>
        <div class="toolbar-right">
          <button class="secondary" @click="toRecord">记录活动</button>
          <button v-if="canOpenAdmin" class="secondary" @click="toAdmin">管理后台</button>
          <button @click="logout">退出登录</button>
        </div>
      </div>
      <p class="subtitle">管理宝宝信息并快速进入记录页面。</p>
    </article>

    <article class="card stack">
      <h2 class="title">新增宝宝</h2>
      <input v-model="newBaby.name" placeholder="宝宝姓名" />
      <input v-model="newBaby.birth_date" type="date" />
      <button class="secondary" @click="createBaby">保存</button>
      <p class="note">{{ message }}</p>
    </article>

    <article class="card">
      <h2 class="title">我的宝宝</h2>
      <div class="list">
        <div v-if="!babies.length" class="item">
          <div class="note">还没有宝宝信息，请先新增。</div>
        </div>
        <div v-for="baby in babies" :key="baby.id" class="item">
          <strong>{{ baby.name }}</strong>
          <div class="note">出生日期：{{ baby.birth_date }}</div>
        </div>
      </div>
    </article>
  </section>
</template>
