import axios from 'axios'

export interface DetectParams {
  conf: number
  iou: number
  imgsz?: number
  maxDet?: number
  classes?: number[]
  agnostic?: boolean
  device?: string
  weights?: string
}

export async function detectImages(files: File[], params: DetectParams) {
  const form = new FormData()
  form.append('params', JSON.stringify(params))
  for (const f of files) form.append('images', f)
  const { data } = await axios.post('/api/detect/image', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  return data as { jobId: string }
}

export async function detectVideo(file: File, params: DetectParams) {
  const form = new FormData()
  form.append('params', JSON.stringify(params))
  form.append('video', file)
  const { data } = await axios.post('/api/detect/video', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  return data as { jobId: string }
}

export async function detectStatus(jobId: string) {
  const { data } = await axios.get('/api/detect/status', { params: { jobId } })
  return data as any
}

export async function listDetectFiles(jobId: string) {
  const { data } = await axios.get('/api/detect/files', { params: { jobId } })
  return data as { files: string[] }
}

export function detectFileUrl(jobId: string, name: string) {
  const usp = new URLSearchParams({ jobId, name })
  return `/api/detect/file?${usp.toString()}`
}

export async function startWebcam(params: DetectParams) {
  const form = new FormData()
  form.append('params', JSON.stringify(params))
  const { data } = await axios.post('/api/detect/webcam/start', form)
  return data as { jobId: string }
}

export async function stopWebcam(jobId: string) {
  const form = new FormData()
  form.append('jobId', jobId)
  const { data } = await axios.post('/api/detect/webcam/stop', form)
  return data
}

export function webcamPreviewUrl(jobId: string) {
  const usp = new URLSearchParams({ jobId })
  return `/api/detect/webcam/preview?${usp.toString()}`
}

export function detectZipUrl(jobId: string) {
  const usp = new URLSearchParams({ jobId })
  return `/api/detect/zip?${usp.toString()}`
}

export async function getDetectJson(jobId: string, imageName: string) {
  const { data } = await axios.get('/api/detect/json', { params: { jobId, image: imageName } })
  return data as { boxes: { cls: number, cx: number, cy: number, w: number, h: number, conf?: number }[] }
}


