import axios from 'axios'

export async function getSystemStats() {
  const { data } = await axios.get('/api/system/stats')
  return data as {
    time: number,
    platform: string,
    python: string,
    cpuPercent: number,
    memory: { total: number, available: number, percent: number },
    gpus: { index: number, name: string }[],
    runs: { train: string[], detect: string[] }
  }
}

export async function getJobs(limit = 20) {
  const { data } = await axios.get('/api/jobs', { params: { limit } })
  return data as { items: { id: string, type: string, status: string, createdAt?: number }[] }
}

export async function getClasses() {
  const { data } = await axios.get('/api/classes')
  return data as { names: string[] }
}


