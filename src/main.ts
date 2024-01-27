import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router";
import { createPinia } from 'pinia'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"

import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import ContextMenu from '@imengyu/vue3-context-menu'

import 'vue3-loading-overlay/dist/vue3-loading-overlay.css';
import { useLoading } from 'vue3-loading-overlay';

const app = createApp(App)
app.use(router)
app.use(ContextMenu)
app.use(useLoading)
app.use(createPinia())
app.mount('#app')
