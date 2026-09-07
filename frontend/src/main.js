import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import 'element-plus/dist/index.css'
import './assets/main.css'
import router from './router/index'
import pinia from './store'

createApp(App).use(pinia).use(router).use(ElementPlus, { locale: zhCn }).mount('#app')
