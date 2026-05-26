<template>
  <div>
    <el-container style="height: 100vh;">
      <el-aside width="220px">
        <AppSidebar />
      </el-aside>
      <el-container>
        <el-header height="56px">
          <AppHeader />
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    <AppToaster />
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './components/layout/AppSidebar.vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppToaster from './components/layout/AppToaster.vue'
</script>

<style>
html, body, #app { height: 100%; margin: 0; }
</style>


