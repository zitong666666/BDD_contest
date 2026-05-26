<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card><div class="section-title">CPU 使用率</div><div style="font-size:24px;">{{ stats?.cpuPercent ?? '--' }}%</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="section-title">内存占用</div><div style="font-size:24px;">{{ stats?.memory?.percent ?? '--' }}%</div></el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div class="section-title">GPU</div>
          <div>{{ stats?.gpus?.length ? stats.gpus.map((g: any) => g.name).join(', ') : '未检测到 GPU' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:12px;">
      <el-col :span="12">
        <el-card>
          <template #header>最近作业</template>
          <el-table :data="jobs" size="small">
            <el-table-column prop="id" label="ID" width="220" />
            <el-table-column prop="type" label="类型" width="140" />
            <el-table-column prop="status" label="状态" width="120" />
            <el-table-column prop="createdAt" label="时间" :formatter="fmtTime" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近 runs</template>
          <div v-if="stats">
            <div>训练：{{ stats.runs.train.slice(0,8).join(', ') || '无' }}</div>
            <div style="margin-top:6px;">检测：{{ stats.runs.detect.slice(0,8).join(', ') || '无' }}</div>
          </div>
          <div v-else>加载中...</div>
        </el-card>
      </el-col>
    </el-row>
    <el-divider />
    <el-row :gutter="16">
      <el-col :span="6"><el-button type="primary" @click="$router.push('/train')">开始训练</el-button></el-col>
      <el-col :span="6"><el-button @click="$router.push('/detect/image')">图片检测</el-button></el-col>
      <el-col :span="6"><el-button @click="$router.push('/detect/video')">视频检测</el-button></el-col>
      <el-col :span="6"><el-button @click="$router.push('/detect/webcam')">摄像头检测</el-button></el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSystemStats, getJobs } from '@/api/system'

const stats = ref<any>(null)
const err = ref<string>('')
const jobs = ref<any[]>([])

async function load() {
  try {
    stats.value = await getSystemStats()
    const j = await getJobs(20)
    jobs.value = j.items
  } catch (e: any) {
    err.value = e?.message || '加载失败'
  }
}
onMounted(load)

function fmtTime(_: any, __: any, v: number) { return v ? new Date(v * 1000).toLocaleString() : '' }
</script>


