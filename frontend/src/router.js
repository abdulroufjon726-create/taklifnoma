import { createRouter, createWebHistory } from 'vue-router'

/*
 * Route-level code splitting: mehmon ochadigan taklifnoma sahifasi
 * builder (QR kutubxonasi, butun forma) kodini yuklamaydi — ochilish tez.
 */
const routes = [
  { path: '/', name: 'builder', component: () => import('./views/BuilderView.vue') },
  { path: '/enter', name: 'enter', component: () => import('./views/EnterView.vue') },
  { path: '/i/:code', name: 'invitation', component: () => import('./views/InvitationView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

export default router
