import { createRouter, createWebHistory } from 'vue-router'
import BuilderView from './views/BuilderView.vue'
import EnterView from './views/EnterView.vue'
import InvitationView from './views/InvitationView.vue'

const routes = [
  { path: '/', name: 'builder', component: BuilderView },
  { path: '/enter', name: 'enter', component: EnterView },
  { path: '/i/:code', name: 'invitation', component: InvitationView },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
