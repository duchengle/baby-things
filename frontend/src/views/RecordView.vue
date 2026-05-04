<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import api from '../api'

function getLocalDateString(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function getLocalTimeString(date = new Date()) {
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const babies = ref([])
const timeline = ref([])
const activityItems = ref([])
const selectedActivityItemId = ref(null)
const form = ref({
  baby_id: '',
  note: '',
  happened_date: getLocalDateString(),
  happened_time: getLocalTimeString()
})
const message = ref('')
const day = ref(getLocalDateString())
const deletingId = ref(null)
const activityElapsedMap = ref({})

const timelineStats = computed(() => {
  const counts = new Map()
  const orderMap = new Map(activityItems.value.map((item) => [item.code, item.sort_order]))
  for (const item of timeline.value) {
    const code = item.activity_type
    const label = item.activity_type_name || code
    if (!counts.has(code)) {
      counts.set(code, { code, label, count: 0 })
    }
    counts.get(code).count += 1
  }
  return Array.from(counts.values())
    .filter((item) => item.count > 0)
    .sort((a, b) => {
      const orderA = orderMap.get(a.code) ?? Number.MAX_SAFE_INTEGER
      const orderB = orderMap.get(b.code) ?? Number.MAX_SAFE_INTEGER
      return orderA - orderB || a.label.localeCompare(b.label, 'zh-CN')
    })
})

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

function formatElapsedDuration(lastAt, selectedAt) {
  const from = new Date(lastAt)
  const to = new Date(selectedAt)
  if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) {
    return 'N/A'
  }

  let diffMs = to.getTime() - from.getTime()
  if (diffMs < 0) {
    diffMs = 0
  }

  const totalMinutes = Math.floor(diffMs / 60000)
  const days = Math.floor(totalMinutes / (24 * 60))
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60)
  const minutes = totalMinutes % 60

  const parts = []
  if (days > 0) {
    parts.push(`${days}天`)
  }
  if (hours > 0) {
    parts.push(`${hours}小时`)
  }
  parts.push(`${minutes}分钟`)
  return parts.join('')
}

async function loadActivityElapsed() {
  if (!form.value.baby_id) {
    activityElapsedMap.value = {}
    return
  }

  const selectedAt = buildHappenedAt()
  try {
    const { data } = await api.get('/activities/activity-items-last', {
      params: {
        baby_id: Number(form.value.baby_id),
        happened_before: selectedAt
      }
    })

    const elapsed = {}
    for (const row of data) {
      elapsed[row.code] = row.last_happened_at
        ? formatElapsedDuration(row.last_happened_at, selectedAt)
        : 'N/A'
    }
    for (const item of activityItems.value) {
      if (!elapsed[item.code]) {
        elapsed[item.code] = 'N/A'
      }
    }
    activityElapsedMap.value = elapsed
  } catch {
    const fallback = {}
    for (const item of activityItems.value) {
      fallback[item.code] = 'N/A'
    }
    activityElapsedMap.value = fallback
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

async function setCurrentTime() {
  const now = new Date()
  const currentDate = getLocalDateString(now)
  form.value.happened_date = currentDate
  form.value.happened_time = getLocalTimeString(now)
  day.value = currentDate
  await loadTimeline()
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

async function deleteActivity(item) {
  const confirmed = window.confirm(`确认删除“${item.activity_type_name || item.activity_type}”这条记录吗？`)
  if (!confirmed) return

  deletingId.value = item.id
  message.value = ''
  try {
    await api.delete(`/activities/${item.id}`)
    await loadTimeline()
    message.value = '记录已删除'
  } catch (err) {
    message.value = err.response?.data?.detail || '删除失败'
  } finally {
    deletingId.value = null
  }
}

onMounted(async () => {
  await loadActivityItems()
  await loadBabies()
  await loadActivityElapsed()
  await loadTimeline()
})

watch(
  [() => form.value.baby_id, () => form.value.happened_date, () => form.value.happened_time],
  () => {
    loadActivityElapsed()
  }
)
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
          <span class="icon-btn-title">{{ item.display_name }}</span>
          <span class="icon-btn-sub">{{ activityElapsedMap[item.code] || 'N/A' }}</span>
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
      <div v-if="timelineStats.length" class="timeline-stats" aria-label="当天活动次数统计">
        <span v-for="stat in timelineStats" :key="stat.label" class="stats-chip">
          {{ stat.label }} {{ stat.count }}次
        </span>
      </div>
      <div class="list">
        <div v-for="item in timeline" :key="item.id" class="item">
          <div class="item-head">
            <strong>{{ item.activity_type_name || item.activity_type }}</strong>
            <button
              type="button"
              class="ghost danger-btn"
              :disabled="deletingId === item.id"
              @click="deleteActivity(item)"
            >
              {{ deletingId === item.id ? '删除中...' : '删除' }}
            </button>
          </div>
          <div class="note">{{ new Date(item.happened_at).toLocaleString() }}</div>
          <div>{{ item.note }}</div>
        </div>
      </div>
    </article>
  </section>
</template>
