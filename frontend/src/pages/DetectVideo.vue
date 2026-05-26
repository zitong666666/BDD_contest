<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <template #header>参数与上传</template>
        <el-form label-width="100px">
          <el-form-item label="conf">
            <el-slider v-model="params.conf" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
          <el-form-item label="iou">
            <el-slider v-model="params.iou" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
          <el-form-item>
            <el-upload drag :auto-upload="false" accept="video/*" :on-change="onAdd">
              <div class="el-upload__text">拖拽视频到此或点击上传</div>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onDetect" :disabled="!rawFile">开始检测</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="16">
      <el-card>
        <template #header>预览</template>
        <div v-if="!jobId">
          <div v-if="!fileUrl">请上传视频</div>
          <video v-else :src="fileUrl" controls style="width:100%" />
        </div>
         <div v-else>
           <div style="margin-bottom:8px; display:flex; align-items:center; gap:12px;">
             <span>作业ID：{{ jobId }} 状态：{{ status }}</span>
             <el-link :href="zipUrl" type="success">打包下载</el-link>
           </div>
          <video v-if="outputVideo" :src="outputVideo" controls style="width:100%" />
          <div v-else>处理中...</div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive, ref, onBeforeUnmount, computed } from 'vue'
import { detectVideo, detectStatus, listDetectFiles, detectFileUrl, detectZipUrl } from '@/api/detect'

const params = reactive({ conf: 0.25, iou: 0.45 })
const fileUrl = ref<string>('')
const rawFile = ref<File | null>(null)
const jobId = ref<string>(localStorage.getItem('currentJobId') || '')
const status = ref<string>('queued')
const outputVideo = ref<string>('')
let timer: any = null
const zipUrl = computed(() => jobId.value ? detectZipUrl(jobId.value) : '#')

function onAdd(file: any) {
  const raw = file.raw as File
  fileUrl.value = URL.createObjectURL(raw)
  rawFile.value = raw
}

async function onDetect() {
  if (!rawFile.value) return
  const res = await detectVideo(rawFile.value, params)
  jobId.value = res.jobId
  startPolling()
}

function startPolling() { stopPolling(); timer = setInterval(refresh, 2000) }
function stopPolling() { if (timer) { clearInterval(timer); timer = null } }
onBeforeUnmount(() => stopPolling())

async function refresh() {
  if (!jobId.value) return
  try {
    const data = await detectStatus(jobId.value)
    status.value = data.status
    if (status.value === 'succeeded') {
      const l = await listDetectFiles(jobId.value)
      const vid = l.files.find(n => /\.(mp4|avi|mov|mkv)$/i.test(n))
      if (vid) outputVideo.value = detectFileUrl(jobId.value, vid)
      stopPolling()
    }
  } catch (e) {
    // 忽略短暂错误
  }
}
</script>


