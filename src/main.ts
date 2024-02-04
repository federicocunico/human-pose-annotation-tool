import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router";
import { createPinia } from 'pinia'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import 'bootstrap-icons/font/bootstrap-icons.css'

import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import ContextMenu from '@imengyu/vue3-context-menu'

import { LoadingPlugin } from 'vue-loading-overlay';
import 'vue-loading-overlay/dist/css/index.css';

const app = createApp(App)
app.use(router)
app.use(ContextMenu)
app.use(LoadingPlugin)
app.use(createPinia())
app.mount('#app')
