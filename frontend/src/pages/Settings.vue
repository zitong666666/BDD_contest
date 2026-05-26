<template>
  <el-card>
    <template #header>系统设置</template>
    <el-form label-width="160px" :model="form">
      <el-form-item label="后端 API 地址">
        <el-input v-model="form.apiBase" placeholder="http://localhost:8000" />
      </el-form-item>
      <el-form-item label="默认权重路径">
        <el-input v-model="form.defaultWeights" placeholder="./yolov5-6.2/weights/yolov5s.pt" />
      </el-form-item>
      <el-form-item label="默认数据集yaml">
        <el-input v-model="form.defaultData" placeholder="./yolov5-6.2/data/mydata.yaml" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary">保存</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  apiBase: 'http://localhost:8000',
  defaultWeights: './yolov5-6.2/weights/yolov5s.pt',
  defaultData: './yolov5-6.2/data/mydata.yaml',
})
</script>


