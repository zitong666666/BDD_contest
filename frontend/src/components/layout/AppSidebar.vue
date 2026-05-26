<template>
  <div class="sidebar">
    <h3 class="brand">YOLOv5 BDD</h3>
    <el-menu
      :default-active="active"
      class="el-menu-vertical-demo"
      router
      unique-opened
    >
      <el-menu-item index="/">
        <span>仪表盘</span>
      </el-menu-item>
      <el-sub-menu index="/train">
        <template #title>训练中心</template>
        <el-menu-item index="/train">训练配置</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="/detect">
        <template #title>检测中心</template>
        <el-menu-item index="/detect/image">图片检测</el-menu-item>
        <el-menu-item index="/detect/video">视频检测</el-menu-item>
        <el-menu-item index="/detect/webcam">摄像头检测</el-menu-item>
      </el-sub-menu>
      <el-menu-item index="/results">
        <span>结果库</span>
      </el-menu-item>
      <el-menu-item index="/settings">
        <span>系统设置</span>
      </el-menu-item>
    </el-menu>
  </div>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = computed(() => route.path)
</script>

<style scoped>
.sidebar { padding: 12px; }
.brand { margin: 6px 0 12px; font-size: 16px; }
</style>


