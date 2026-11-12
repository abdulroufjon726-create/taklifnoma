import { createRouter, createWebHistory } from 'vue-router'

/*
 * Route-level code splitting: mehmon ochadigan taklifnoma sahifasi
 * builder (QR kutubxonasi, butun forma) kodini yuklamaydi — ochilish tez.
 */
const routes = [
  { path: '/', name: 'home', component: () => import('./views/HomeView.vue') },
  { path: '/create', name: 'builder', component: () => import('./views/BuilderView.vue') },
  { path: '/login', name: 'login', component: () => import('./views/LoginView.vue') },
  { path: '/envelopes', name: 'envelopes', component: () => import('./views/EnvelopesView.vue') },
  {
    path: '/envelopes/:code',
    name: 'envelope',
    component: () => import('./views/EnvelopeView.vue'),
  },
  { path: '/account', name: 'account', component: () => import('./views/ProfileView.vue') },
  { path: '/auth', name: 'auth', component: () => import('./views/AuthView.vue') },
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
