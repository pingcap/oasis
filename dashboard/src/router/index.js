import Vue from 'vue'
import Router from 'vue-router'
import HomeView from '@/views/HomeView'
import JobDetailView from '@/views/JobDetailView'
import ModelTemplatesView from '@/views/ModelTemplatesView'

Vue.use(Router)

const NotFoundView = Vue.component('NotFoundView', {
  template: '<h1>...Ops, 404</h1>'
})

export default new Router({
  mode: 'history',
  routes: [
    { path: '/', redirect: '/home' },
    {
      path: '/404',
      name: 'NotFoundView',
      component: NotFoundView
    },
    {
      path: '/home',
      name: 'HomeView',
      component: HomeView
    },
    {
      path: '/detail',
      name: 'JobDetailView',
      component: JobDetailView
    },
    {
      path: '/model_templates',
      name: 'ModelTemplatesView',
      component: ModelTemplatesView
    }
  ]
})
