import { createRouter, createWebHashHistory } from "vue-router";
import Selector from "@/components/Selector.vue";
import MainVue from "./components/Main.vue";
import SingleJointMainVue from "./components/single-joint/SingleJointMain.vue";


const routes = [
    { path: '/', component: Selector },
    { path: '/annotate', component: MainVue },
    { path: '/annotate-joints', component: SingleJointMainVue },
]

export default createRouter({
    history: createWebHashHistory(),
    routes, // short for `routes: routes`
})
