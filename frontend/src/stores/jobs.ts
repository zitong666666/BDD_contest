import { defineStore } from 'pinia'

export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'stopped'

export interface JobItem {
  id: string
  type: 'train' | 'detect-image' | 'detect-video' | 'detect-webcam'
  status: JobStatus
  progress?: number
  createdAt: number
  meta?: Record<string, unknown>
}

export const useJobsStore = defineStore('jobs', {
  state: () => ({
    items: [] as JobItem[],
  }),
  actions: {
    upsert(job: JobItem) {
      const idx = this.items.findIndex(j => j.id === job.id)
      if (idx >= 0) this.items[idx] = { ...this.items[idx], ...job }
      else this.items.unshift(job)
      try { localStorage.setItem('currentJobId', job.id) } catch {}
    },
    remove(id: string) {
      this.items = this.items.filter(j => j.id !== id)
      try { localStorage.removeItem('currentJobId') } catch {}
    },
  }
})


