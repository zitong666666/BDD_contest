import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Dashboard', component: () => import('../pages/Dashboard.vue') },
  { path: '/train', name: 'Train', component: () => import('../pages/Train.vue') },
  { path: '/detect/image', name: 'DetectImage', component: () => import('../pages/DetectImage.vue') },
  { path: '/detect/video', name: 'DetectVideo', component: () => import('../pages/DetectVideo.vue') },
  { path: '/detect/webcam', name: 'DetectWebcam', component: () => import('../pages/DetectWebcam.vue') },
  { path: '/results', name: 'Results', component: () => import('../pages/Results.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../pages/Settings.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router


