<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api'

const router = useRouter()
const pendingUsers = ref([])
const users = ref([])
const babies = ref([])
const activityItems = ref([])
const message = ref('')

const grantForm = reactive({
  babyId: '',
  userId: '',
  can_view: true,
  can_record: true
})

const itemForm = reactive({
  code: '',
  display_name: '',
  sort_order: 100,
  is_enabled: true
})

async function loadData() {
  message.value = ''
  try {
    const [pendingResp, usersResp, babiesResp, itemsResp] = await Promise.all([
      api.get('/admin/users/pending'),
      api.get('/admin/users'),
      api.get('/babies'),
      api.get('/admin/activity-items')
    ])
    pendingUsers.value = pendingResp.data
    users.value = usersResp.data.filter((item) => item.role !== 'admin')
    babies.value = babiesResp.data
    activityItems.value = itemsResp.data
  } catch (err) {
    if (err.response?.status === 403) {
      message.value = '该页面仅管理员可访问。'
    } else {
      message.value = err.response?.data?.detail || '加载管理数据失败'
    }
  }
}

async function createActivityItem() {
  message.value = ''
  if (!itemForm.code || !itemForm.display_name) {
    message.value = '请填写活动编码和活动名称'
    return
  }

  try {
    await api.post('/admin/activity-items', {
      code: itemForm.code,
      display_name: itemForm.display_name,
      sort_order: Number(itemForm.sort_order || 100),
      is_enabled: itemForm.is_enabled
    })
    itemForm.code = ''
    itemForm.display_name = ''
    itemForm.sort_order = 100
    itemForm.is_enabled = true
    activityItems.value = (await api.get('/admin/activity-items')).data
    message.value = '活动类型创建成功'
  } catch (err) {
    message.value = err.response?.data?.detail || '创建活动类型失败'
  }
}

async function saveActivityItem(item) {
  message.value = ''
  try {
    await api.put(`/admin/activity-items/${item.id}`, {
      code: item.code,
      display_name: item.display_name,
      sort_order: Number(item.sort_order),
      is_enabled: item.is_enabled
    })
    message.value = '活动类型已更新'
  } catch (err) {
    message.value = err.response?.data?.detail || '更新活动类型失败'
  }
}

async function toggleActivityItem(item) {
  message.value = ''
  try {
    await api.put(`/admin/activity-items/${item.id}`, {
      is_enabled: !item.is_enabled
    })
    item.is_enabled = !item.is_enabled
    message.value = item.is_enabled ? '活动类型已启用' : '活动类型已停用'
  } catch (err) {
    message.value = err.response?.data?.detail || '更新状态失败'
  }
}

async function deleteActivityItem(itemId) {
  message.value = ''
  try {
    await api.delete(`/admin/activity-items/${itemId}`)
    activityItems.value = activityItems.value.filter((item) => item.id !== itemId)
    message.value = '活动类型已删除'
  } catch (err) {
    message.value = err.response?.data?.detail || '删除活动类型失败'
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

    <article class="card stack">
      <h2 class="title">活动类型管理</h2>
      <p class="note">支持新增、编辑、启停、排序和删除。删除仅对未被活动记录引用的类型生效。</p>

      <div class="grid grid-2">
        <input v-model="itemForm.code" placeholder="活动编码（例如 feeding）" />
        <input v-model="itemForm.display_name" placeholder="活动名称" />
      </div>

      <div class="grid grid-2">
        <input v-model="itemForm.sort_order" type="number" placeholder="排序值（越小越靠前）" />
        <label class="check-row">
          <input v-model="itemForm.is_enabled" type="checkbox" />
          <span>创建后启用</span>
        </label>
      </div>

      <button class="secondary" @click="createActivityItem">新增活动类型</button>

      <div class="list">
        <div v-if="!activityItems.length" class="item">
          <div class="note">暂无活动类型。</div>
        </div>

        <div v-for="item in activityItems" :key="item.id" class="item stack">
          <div class="grid grid-2">
            <input v-model="item.code" />
            <input v-model="item.display_name" />
          </div>
          <div class="grid grid-2">
            <input v-model="item.sort_order" type="number" />
            <div class="row-between">
              <span class="note">状态：{{ item.is_enabled ? '启用' : '停用' }}</span>
              <label class="check-row">
                <input v-model="item.is_enabled" type="checkbox" />
                <span>启用</span>
              </label>
            </div>
          </div>

          <div class="toolbar-right">
            <button class="secondary" @click="saveActivityItem(item)">保存</button>
            <button class="ghost" @click="toggleActivityItem(item)">{{ item.is_enabled ? '停用' : '启用' }}</button>
            <button @click="deleteActivityItem(item.id)">删除</button>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>
