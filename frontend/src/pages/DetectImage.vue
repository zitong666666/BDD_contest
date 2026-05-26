<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <template #header>参数</template>
         <el-form label-width="100px">
          <el-form-item label="conf">
            <el-slider v-model="params.conf" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
          <el-form-item label="iou">
            <el-slider v-model="params.iou" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
           <el-form-item label="类别过滤">
             <el-select v-model="classFilter" multiple collapse-tags placeholder="全部" style="width:100%">
               <el-option v-for="(n, idx) in classes" :key="idx" :label="n" :value="idx" />
             </el-select>
           </el-form-item>
           <el-form-item>
             <el-checkbox v-model="showLabel">显示标签</el-checkbox>
           </el-form-item>
          <el-form-item label="imgsz">
            <el-input-number v-model="params.imgsz" :min="320" :max="1280" :step="32" />
          </el-form-item>
          <el-form-item>
            <el-upload drag multiple :auto-upload="false" :on-change="onAdd">
              <i class="el-icon-upload" />
              <div class="el-upload__text">拖拽图片到此或点击上传</div>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onDetect" :disabled="files.length===0">开始检测</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="16">
      <el-card>
        <template #header>预览</template>
        <div v-if="!jobId">
          <div v-if="files.length === 0">请先上传图片</div>
          <el-row :gutter="12">
            <el-col v-for="(f, idx) in files" :key="idx" :span="12">
              <img :src="f.url" style="width:100%;" />
            </el-col>
          </el-row>
        </div>
         <div v-else>
           <div style="margin-bottom:8px; display:flex; align-items:center; gap:12px;">
             <span>作业ID：{{ jobId }} 状态：{{ status }}</span>
             <el-link :href="zipUrl" type="success">打包下载</el-link>
           </div>
           <el-row :gutter="12">
             <el-col v-for="(name, idx) in outputs" :key="idx" :span="12">
               <div style="position:relative;">
                 <img :src="fileUrl(name)" style="width:100%; display:block;" @load="onImgLoad($event, name)" />
                 <canvas :ref="setCanvasRef(name)" style="position:absolute; left:0; top:0; width:100%; height:100%; pointer-events:none;"></canvas>
               </div>
             </el-col>
           </el-row>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive, ref, onBeforeUnmount, computed, onMounted } from 'vue'
import { detectImages, detectStatus, listDetectFiles, detectFileUrl, detectZipUrl, getDetectJson } from '@/api/detect'
import { getClasses } from '@/api/system'

const params = reactive({ conf: 0.25, iou: 0.45, imgsz: 640 })
const files = ref<{ url: string, raw?: File }[]>([])
const jobId = ref<string>(localStorage.getItem('currentJobId') || '')
const status = ref<string>('queued')
const outputs = ref<string[]>([])
let timer: any = null
const zipUrl = computed(() => jobId.value ? detectZipUrl(jobId.value) : '#')
const canvasMap = new Map<string, HTMLCanvasElement>()
const classes = ref<string[]>([])
const classFilter = ref<number[]>([])
const showLabel = ref<boolean>(true)

onMounted(async () => {
  try { const r = await getClasses(); classes.value = r.names || [] } catch {}
})

function onAdd(file: any) {
  const raw = file.raw as File
  const url = URL.createObjectURL(raw)
  files.value.push({ url, raw })
}

async function onDetect() {
  const rawFiles = files.value.map(f => f.raw!).filter(Boolean)
  const res = await detectImages(rawFiles as File[], params)
  jobId.value = res.jobId
  startPolling()
}

function startPolling() {
  stopPolling(); timer = setInterval(refresh, 2000)
}
function stopPolling() { if (timer) { clearInterval(timer); timer = null } }
onBeforeUnmount(() => stopPolling())

async function refresh() {
  if (!jobId.value) return
  try {
    const data = await detectStatus(jobId.value)
    status.value = data.status
    if (status.value === 'succeeded') {
      const l = await listDetectFiles(jobId.value)
      outputs.value = l.files.filter(n => /\.(jpg|png|jpeg)$/i.test(n))
      // 绘制叠加框
      for (const name of outputs.value) {
        await drawBoxes(name)
      }
      stopPolling()
    }
  } catch (e) {
    // job 不存在或后端重启时，短暂忽略错误，继续轮询
  }
}

function fileUrl(name: string) { return detectFileUrl(jobId.value, name) }

function setCanvasRef(name: string) {
  return (el: HTMLCanvasElement | null) => { if (el) canvasMap.set(name, el) }
}

async function onImgLoad(e: Event, name: string) {
  await drawBoxes(name)
}

async function drawBoxes(name: string) {
  if (!jobId.value) return
  const canvas = canvasMap.get(name)
  const imgEl = (canvas?.previousSibling as HTMLImageElement) || null
  if (!canvas || !imgEl) return
  const rect = imgEl.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height
  const ctx = canvas.getContext('2d')!
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  try {
    const data = await getDetectJson(jobId.value, name)
    for (const b of data.boxes) {
      if (classFilter.value.length && !classFilter.value.includes(b.cls)) continue
      // b 为归一化坐标，转为像素
      const x = (b.cx - b.w / 2) * canvas.width
      const y = (b.cy - b.h / 2) * canvas.height
      const w = b.w * canvas.width
      const h = b.h * canvas.height
      ctx.strokeStyle = '#22c55e'
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, w, h)
      if (showLabel.value) {
        const cname = classes.value[b.cls] ?? `cls:${b.cls}`
        const label = `${cname}${b.conf != null ? ' ' + (b.conf*100).toFixed(1) + '%' : ''}`
        ctx.fillStyle = 'rgba(34,197,94,0.85)'
        ctx.fillRect(x, y - 18, ctx.measureText(label).width + 10, 18)
        ctx.fillStyle = '#fff'
        ctx.font = '12px system-ui'
        ctx.fillText(label, x + 4, y - 5)
      }
    }
  } catch {}
}
</script>


