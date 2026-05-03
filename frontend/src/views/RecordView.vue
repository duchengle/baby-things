<script setup>
import { onMounted, ref } from 'vue'

import api from '../api'

const babies = ref([])
const timeline = ref([])
const activityItems = ref([])
const selectedActivityItemId = ref(null)
const form = ref({
  baby_id: '',
  note: '',
  happened_date: new Date().toISOString().slice(0, 10),
  happened_time: new Date().toTimeString().slice(0, 5)
})
const message = ref('')
const day = ref(new Date().toISOString().slice(0, 10))

async function loadBabies() {
  const { data } = await api.get('/babies')
  babies.value = data
  if (!form.value.baby_id && babies.value.length) {
    form.value.baby_id = babies.value[0].id
  }
}

async function loadActivityItems() {
  const { data } = await api.get('/activities/activity-items')
  activityItems.value = data
  if (!selectedActivityItemId.value && data.length) {
    selectedActivityItemId.value = data[0].id
  }
}

async function saveActivity() {
  if (!form.value.baby_id) {
    message.value = '请先选择宝宝'
    return
  }
  if (!selectedActivityItemId.value) {
    message.value = '请先选择活动类型'
    return
  }

  const happenedAt = buildHappenedAt()
  message.value = ''
  try {
    await api.post('/activities', {
      baby_id: Number(form.value.baby_id),
      activity_item_id: Number(selectedActivityItemId.value),
      note: form.value.note,
      happened_at: happenedAt,
      images: []
    })
    form.value.note = ''
    form.value.happened_time = new Date().toTimeString().slice(0, 5)
    await loadTimeline()
  } catch (err) {
    message.value = err.response?.data?.detail || '保存失败'
  }
}

function buildHappenedAt() {
  if (form.value.happened_date && form.value.happened_time) {
    return `${form.value.happened_date}T${form.value.happened_time}:00`
  }
  if (form.value.happened_date) {
    return `${form.value.happened_date}T00:00:00`
  }
  return new Date().toISOString()
}

function setCurrentTime() {
  const now = new Date()
  form.value.happened_date = now.toISOString().slice(0, 10)
  form.value.happened_time = now.toTimeString().slice(0, 5)
}

async function loadTimeline() {
  if (!form.value.baby_id) return
  const dayIso = `${day.value}T00:00:00`
  const { data } = await api.get('/activities/timeline', {
    params: {
      baby_id: Number(form.value.baby_id),
      day: dayIso
    }
  })
  timeline.value = data
}

onMounted(async () => {
  await loadActivityItems()
  await loadBabies()
  await loadTimeline()
})
</script>

<template>
  <section class="stack record-compact">
    <article class="card stack">
      <h1 class="title">活动记录</h1>

      <div class="grid grid-2 record-head-row">
        <select v-model="form.baby_id" @change="loadTimeline">
          <option value="" disabled>选择宝宝</option>
          <option v-for="baby in babies" :key="baby.id" :value="baby.id">{{ baby.name }}</option>
        </select>
        <input v-model="day" type="date" @change="loadTimeline" />
      </div>

      <div class="icon-grid">
        <button
          v-for="item in activityItems"
          :key="item.id"
          class="icon-btn"
          :style="item.id === selectedActivityItemId ? 'outline: 3px solid #ff956f;' : ''"
          @click="selectedActivityItemId = item.id"
        >
          {{ item.display_name }}
        </button>
      </div>

      <textarea v-model="form.note" rows="3" placeholder="备注"></textarea>
      <div class="datetime-grid record-datetime-row">
        <label class="picker-group">
          <span class="picker-label">活动日期</span>
          <input v-model="form.happened_date" type="date" />
        </label>
        <label class="picker-group">
          <span class="picker-label">活动时间</span>
          <div class="time-row">
            <input v-model="form.happened_time" type="time" step="60" />
            <button type="button" class="ghost time-now-btn" @click="setCurrentTime">当前时间</button>
          </div>
        </label>
      </div>
      <button class="secondary" @click="saveActivity">保存记录</button>
      <p class="note">{{ message }}</p>
    </article>

    <article class="card">
      <h2 class="title">每日时间轴</h2>
      <div class="list">
        <div v-for="item in timeline" :key="item.id" class="item">
          <strong>{{ item.activity_type_name || item.activity_type }}</strong>
          <div class="note">{{ new Date(item.happened_at).toLocaleString() }}</div>
          <div>{{ item.note }}</div>
        </div>
      </div>
    </article>
  </section>
</template>
