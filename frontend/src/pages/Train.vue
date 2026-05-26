<template>
  <el-row :gutter="16">
    <el-col :span="10">
      <el-card>
        <template #header>训练配置</template>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
          <el-form-item label="参数模板">
            <el-radio-group v-model="preset" @change="applyPreset">
              <el-radio label="light">轻量</el-radio>
              <el-radio label="balanced">平衡</el-radio>
              <el-radio label="accurate">高精度</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="form.model" placeholder="选择模型">
              <el-option label="yolov5s" value="yolov5s" />
              <el-option label="yolov5m" value="yolov5m" />
              <el-option label="yolov5l" value="yolov5l" />
              <el-option label="yolov5x" value="yolov5x" />
            </el-select>
          </el-form-item>
          <el-form-item label="权重" prop="weights">
            <el-input v-model="form.weights" placeholder="./yolov5-6.2/weights/yolov5s.pt" />
          </el-form-item>
          <el-form-item label="数据集yaml" prop="data">
            <el-input v-model="form.data" placeholder="./yolov5-6.2/data/mydata.yaml" />
          </el-form-item>
          <el-form-item label="epochs" prop="epochs">
            <el-input-number v-model="form.epochs" :min="1" :max="500" />
          </el-form-item>
          <el-form-item label="batch" prop="batch">
            <el-input-number v-model="form.batch" :min="1" :max="256" />
          </el-form-item>
          <el-form-item label="imgsz" prop="imgsz">
            <el-input-number v-model="form.imgsz" :min="320" :max="1280" :step="32" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onValidateAndStart">开始训练</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="14">
      <el-card>
        <template #header>
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <span>训练监控</span>
            <div>
              <el-button size="small" @click="refresh">刷新</el-button>
              <el-button size="small" type="danger" @click="onStop" :disabled="!jobId">停止训练</el-button>
            </div>
          </div>
        </template>
        <el-tabs v-model="tab">
          <el-tab-pane label="日志" name="logs">
            <div style="white-space: pre-wrap; background:#fff; color:#333; border:1px solid #e5e7eb; padding:8px; height:220px; overflow:auto;">
              {{ logs.join('') || '等待日志...' }}
            </div>
          </el-tab-pane>
          <el-tab-pane label="曲线" name="charts">
            <div id="chart" style="height:280px;"></div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive, ref, onBeforeUnmount, onMounted } from 'vue'
import { startTrain, getTrainStatus, stopTrain } from '@/api/train'
import { getTrainMetrics } from '@/api/train'
import * as echarts from 'echarts'

const form = reactive({
  model: 'yolov5s',
  weights: './yolov5-6.2/weights/yolov5s.pt',
  data: './yolov5-6.2/data/mydata.yaml',
  epochs: 100,
  batch: 16,
  imgsz: 640,
})

const jobId = ref<string>(localStorage.getItem('currentJobId') || '')
const logs = ref<string[]>([])
let timer: any = null
let chart: echarts.ECharts | null = null
const tab = ref<'logs' | 'charts'>('logs')
const formRef = ref()
const preset = ref<'light' | 'balanced' | 'accurate'>('balanced')
const rules = {
  weights: [{ required: true, message: '请填写权重路径', trigger: 'blur' }],
  data: [{ required: true, message: '请填写数据集yaml路径', trigger: 'blur' }],
  epochs: [{ type: 'number', min: 1, max: 500, message: '1-500', trigger: 'change' }],
  batch: [{ type: 'number', min: 1, max: 256, message: '1-256', trigger: 'change' }],
  imgsz: [{ type: 'number', min: 320, max: 1280, message: '320-1280', trigger: 'change' }],
} as any

async function onStart() {
  const res = await startTrain(form as any)
  jobId.value = res.jobId
  startPolling()
}

function onValidateAndStart() {
  (formRef.value as any).validate((ok: boolean) => { if (ok) onStart() })
}

function startPolling() {
  stopPolling()
  timer = setInterval(() => { refresh(); refreshMetrics() }, 2000)
}

function stopPolling() {
  if (timer) { clearInterval(timer); timer = null }
}

async function refresh() {
  if (!jobId.value) return
  const data = await getTrainStatus(jobId.value)
  logs.value = data.logs || []
  if (data.status === 'succeeded' || data.status === 'failed') stopPolling()
}

onBeforeUnmount(() => stopPolling())

function applyPreset() {
  if (preset.value === 'light') {
    form.model = 'yolov5s'
    form.batch = 32
    form.imgsz = 640
    form.epochs = 50
  } else if (preset.value === 'balanced') {
    form.model = 'yolov5m'
    form.batch = 16
    form.imgsz = 640
    form.epochs = 100
  } else {
    form.model = 'yolov5l'
    form.batch = 8
    form.imgsz = 960
    form.epochs = 150
  }
}

onMounted(() => {
  const el = document.getElementById('chart')
  if (el) {
    chart = echarts.init(el)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['train/box_loss', 'train/obj_loss', 'metrics/mAP_0.5'] },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [
        { name: 'train/box_loss', type: 'line', data: [] },
        { name: 'train/obj_loss', type: 'line', data: [] },
        { name: 'metrics/mAP_0.5', type: 'line', data: [] },
      ]
    })
  }
})

async function refreshMetrics() {
  if (!jobId.value || !chart) return
  const m = await getTrainMetrics(jobId.value)
  const xs: string[] = []
  const box: number[] = []
  const obj: number[] = []
  const map50: number[] = []
  for (const r of m.rows) {
    xs.push((r['epoch'] ?? '').toString())
    box.push(Number(r['box_loss'] ?? r['train/box_loss'] ?? 0))
    obj.push(Number(r['obj_loss'] ?? r['train/obj_loss'] ?? 0))
    map50.push(Number(r['metrics/mAP_0.5'] ?? r['map50'] ?? 0))
  }
  chart.setOption({ xAxis: { data: xs }, series: [{ data: box }, { data: obj }, { data: map50 }] })
}

async function onStop() {
  if (!jobId.value) return
  try {
    await stopTrain(jobId.value)
  } catch (e) {}
}
</script>


