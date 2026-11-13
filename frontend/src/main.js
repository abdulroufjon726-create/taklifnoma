import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import { pruneCaches, warmUp } from './api.js'
import './assets/main.css'

createApp(App).use(router).mount('#app')

// Render bepul tarifi uxlab qolishi mumkin — har qanday sahifa ochilishida
// backendni oldindan uyg'otamiz (taklifnoma havolasi tezroq yuklanadi).
pruneCaches()
warmUp()
