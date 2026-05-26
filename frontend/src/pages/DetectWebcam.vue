<template>
  <el-card>
    <template #header>摄像头检测</template>
    <el-form label-width="100px">
      <el-form-item label="参数">
        <div style="display:flex; gap:12px; align-items:center;">
          <span>conf</span>
          <el-slider v-model="params.conf" :min="0" :max="1" :step="0.01" style="width:200px" />
          <span>iou</span>
          <el-slider v-model="params.iou" :min="0" :max="1" :step="0.01" style="width:200px" />
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onStart" :disabled="isRunning">开始检测</el-button>
        <el-button @click="onStop" :disabled="!isRunning">停止检测</el-button>
      </el-form-item>
    </el-form>
    
    <div v-if="!isRunning" style="color:#888; text-align:center; padding:40px;">
      点击"开始检测"后，系统将使用摄像头进行实时检测
    </div>
    
    <div v-else style="text-align:center; padding:20px;">
      <div style="margin-bottom:10px; color:#666;">
        检测状态: {{ status }} | 作业ID: {{ jobId }}
      </div>
      <div v-if="previewUrl" style="border:2px solid #ddd; display:inline-block;">
        <img :src="previewUrl" style="max-width:100%; max-height:400px; background:#000;" @error="onPreviewError" />
      </div>
      <div v-else style="color:#999; padding:20px;">
        等待检测结果...
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { startWebcam, stopWebcam, webcamPreviewUrl, detectStatus } from '@/api/detect'

const params = ref({ conf: 0.25, iou: 0.45, imgsz: 640 })
const jobId = ref<string>('')
const status = ref<string>('')
const tick = ref<number>(0)
let timer: any = null

const isRunning = computed(() => !!jobId.value && status.value !== 'failed')

async function onStart() {
  try {
    const res = await startWebcam(params.value)
    jobId.value = res.jobId
    status.value = 'starting'
    startPolling()
  } catch (error) {
    console.error('启动摄像头检测失败:', error)
    status.value = 'failed'
  }
}

async function onStop() {
  if (!jobId.value) return
  try {
    await stopWebcam(jobId.value)
  } catch (error) {
    console.error('停止摄像头检测失败:', error)
  } finally {
    stopPolling()
    jobId.value = ''
    status.value = ''
  }
}

async function startPolling() {
  stopPolling()
  timer = setInterval(async () => {
    if (!jobId.value) return
    
    try {
      const res = await detectStatus(jobId.value)
      status.value = res.status || 'running'
      tick.value++
      
      if (res.status === 'failed' || res.status === 'completed') {
        stopPolling()
      }
    } catch (error) {
      console.error('轮询状态失败:', error)
    }
  }, 2000)
}

function stopPolling() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

onBeforeUnmount(() => stopPolling())

const previewUrl = computed(() => {
  if (!jobId.value) return ''
  return `${webcamPreviewUrl(jobId.value)}&t=${tick.value}`
})

function onPreviewError() {
  // 静默处理图片加载错误，继续轮询
}
</script>


