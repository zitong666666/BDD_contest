import axios from 'axios'

export async function listResults(kind: 'all' | 'train' | 'detect' = 'all') {
  const { data } = await axios.get('/api/results/list', { params: { kind } })
  return data as { items: { type: string, name: string, mtime: number }[] }
}

export async function listResultFiles(kind: 'train' | 'detect', name: string) {
  const { data } = await axios.get('/api/results/files', { params: { kind, name } })
  return data as { files: string[] }
}

export function resultFileUrl(kind: 'train' | 'detect', name: string, file: string) {
  const usp = new URLSearchParams({ kind, name, file })
  return `/api/results/file?${usp.toString()}`
}


