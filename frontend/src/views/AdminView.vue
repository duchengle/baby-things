<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api'

const router = useRouter()
const pendingUsers = ref([])
const users = ref([])
const babies = ref([])
const message = ref('')

const grantForm = reactive({
  babyId: '',
  userId: '',
  can_view: true,
  can_record: true
})

async function loadData() {
  message.value = ''
  try {
    const [pendingResp, usersResp, babiesResp] = await Promise.all([
      api.get('/admin/users/pending'),
      api.get('/admin/users'),
      api.get('/babies')
    ])
    pendingUsers.value = pendingResp.data
    users.value = usersResp.data.filter((item) => item.role !== 'admin')
    babies.value = babiesResp.data
  } catch (err) {
    if (err.response?.status === 403) {
      message.value = '该页面仅管理员可访问。'
    } else {
      message.value = err.response?.data?.detail || '加载管理数据失败'
    }
  }
}

async function approveUser(userId) {
  message.value = ''
  try {
    await api.post(`/admin/users/${userId}/approve`)
    await loadData()
    message.value = '用户审核通过'
  } catch (err) {
    message.value = err.response?.data?.detail || '审核失败'
  }
}

async function grantAccess() {
  message.value = ''
  if (!grantForm.babyId || !grantForm.userId) {
    message.value = '请选择宝宝和用户'
    return
  }

  try {
    await api.post(`/babies/${grantForm.babyId}/access`, {
      user_id: Number(grantForm.userId),
      can_view: grantForm.can_view,
      can_record: grantForm.can_record
    })
    message.value = '宝宝权限已更新'
  } catch (err) {
    message.value = err.response?.data?.detail || '授权失败'
  }
}

function backToHome() {
  router.push('/dashboard')
}

onMounted(loadData)
</script>

<template>
  <section class="stack">
    <article class="card stack">
      <div class="header-row">
        <h1 class="title">管理后台</h1>
        <button class="ghost" @click="backToHome">返回主页</button>
      </div>
      <p class="subtitle">审核注册用户，并设置谁可以查看或记录宝宝活动。</p>
      <p class="note">{{ message }}</p>
    </article>

    <article class="card">
      <h2 class="title">待审核用户</h2>
      <div class="list">
        <div v-if="!pendingUsers.length" class="item">
          <div class="note">暂无待审核用户。</div>
        </div>
        <div v-for="user in pendingUsers" :key="user.id" class="item row-between">
          <div>
            <strong>{{ user.username }}</strong>
            <div class="note">状态：待审核</div>
          </div>
          <button @click="approveUser(user.id)">通过</button>
        </div>
      </div>
    </article>

    <article class="card stack">
      <h2 class="title">宝宝权限授权</h2>
      <div class="grid grid-2">
        <select v-model="grantForm.babyId">
          <option value="" disabled>选择宝宝</option>
          <option v-for="baby in babies" :key="baby.id" :value="baby.id">{{ baby.name }}</option>
        </select>

        <select v-model="grantForm.userId">
          <option value="" disabled>选择用户</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.username }}（{{ user.is_approved ? '已通过' : '待审核' }}）
          </option>
        </select>
      </div>

      <div class="grid grid-2">
        <label class="check-row">
          <input v-model="grantForm.can_view" type="checkbox" />
          <span>可查看</span>
        </label>
        <label class="check-row">
          <input v-model="grantForm.can_record" type="checkbox" />
          <span>可记录</span>
        </label>
      </div>

      <button class="secondary" @click="grantAccess">保存授权</button>
    </article>
  </section>
</template>
