// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'

import FontAwesomeIcon from '@fortawesome/vue-fontawesome'
import fontawesome from '@fortawesome/fontawesome'

import faHandRock from '@fortawesome/fontawesome-free-solid/faHandRock'
import faHandPaper from '@fortawesome/fontawesome-free-solid/faHandPaper'
import faHandScissors from '@fortawesome/fontawesome-free-solid/faHandScissors'
import faDesktop from '@fortawesome/fontawesome-free-solid/faDesktop'
import faSmile from '@fortawesome/fontawesome-free-solid/faSmile'
import faSync from '@fortawesome/fontawesome-free-solid/faSync'
import faBalanceScale from '@fortawesome/fontawesome-free-solid/faBalanceScale'

fontawesome.library.add(faHandRock, faHandPaper, faHandScissors, faDesktop, faSmile, faSync, faBalanceScale)

Vue.config.productionTip = false
Vue.component('font-awesome-icon', FontAwesomeIcon)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  components: { App },
  template: '<App/>'
})
