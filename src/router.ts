import { createRouter, createWebHashHistory } from "vue-router";
import Selector from "@/components/Selector.vue";
import MainVue from "./components/Main.vue";


const routes = [
    { path: '/', component: Selector },
    { path: '/annotate', component: MainVue },
]

export default createRouter({
    history: createWebHashHistory(),
    routes, // short for `routes: routes`
})
