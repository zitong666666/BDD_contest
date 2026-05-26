import axios from 'axios'

export interface StartTrainPayload {
  model: string
  weights: string
  data: string
  epochs: number
  batch: number
  imgsz: number
}

export async function startTrain(payload: StartTrainPayload) {
  const { data } = await axios.post('/api/train/start', payload)
  return data as { jobId: string }
}

export async function getTrainStatus(jobId: string) {
  const { data } = await axios.get('/api/train/status', { params: { jobId } })
  return data as any
}

export async function stopTrain(jobId: string) {
  const { data } = await axios.post('/api/train/stop', { jobId })
  return data
}

export async function getTrainMetrics(jobId: string) {
  const { data } = await axios.get('/api/train/metrics', { params: { jobId } })
  return data as { rows: Record<string, string>[] }
}


