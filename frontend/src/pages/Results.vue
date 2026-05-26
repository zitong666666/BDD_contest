<template>
  <div>
    <el-card>
      <template #header>结果库</template>
      <div style="margin-bottom:12px; display:flex; gap:12px; align-items:center;">
        <el-select v-model="kind" style="width:200px">
          <el-option label="全部" value="all" />
          <el-option label="训练" value="train" />
          <el-option label="检测" value="detect" />
        </el-select>
        <el-button @click="refresh" type="primary">刷新</el-button>
      </div>
      <el-table :data="items" style="width:100%" @row-click="onRow">
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="mtime" label="更新时间" :formatter="fmtTime" width="200" />
      </el-table>
    </el-card>

    <el-drawer v-model="open" :title="detailTitle" size="50%">
      <div v-if="files.length === 0">暂无文件</div>
      <div v-else>
        <div v-for="(f, idx) in files" :key="idx" style="margin-bottom:12px;">
          <div style="margin-bottom:4px;">{{ f }}</div>
          <img v-if="isImage(f)" :src="fileUrl(f)" style="width:100%;" />
          <video v-else-if="isVideo(f)" :src="fileUrl(f)" controls style="width:100%" />
          <el-link v-else :href="fileUrl(f)" target="_blank">下载</el-link>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { listResults, listResultFiles, resultFileUrl } from '@/api/results'

const kind = ref<'all' | 'train' | 'detect'>('all')
const items = ref<{ type: 'train' | 'detect', name: string, mtime: number }[]>([])
const open = ref(false)
const current = ref<{ type: 'train' | 'detect', name: string } | null>(null)
const files = ref<string[]>([])

function fmtTime(_: any, __: any, v: number) { return new Date(v * 1000).toLocaleString() }

async function refresh() {
  const res = await listResults(kind.value)
  items.value = res.items as any
}
refresh()

async function onRow(row: any) {
  current.value = { type: row.type, name: row.name }
  const r = await listResultFiles(row.type, row.name)
  files.value = r.files
  open.value = true
}

function isImage(n: string) { return /\.(jpg|jpeg|png|gif)$/i.test(n) }
function isVideo(n: string) { return /\.(mp4|avi|mov|mkv)$/i.test(n) }
const detailTitle = computed(() => current.value ? `${current.value.type} - ${current.value.name}` : '')

function fileUrl(n: string) { return resultFileUrl(current!.value!.type, current!.value!.name, n) }
</script>


