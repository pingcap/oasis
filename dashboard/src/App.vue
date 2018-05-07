<template>
  <div id="app" class="app-container">
    <headerComponent/>
    <router-view></router-view>
  </div>
</template>

<script>
import headerComponent from './components/header'

export default {
  name: 'app', 
  components: {
    headerComponent
  }
}
</script>

<style lang="scss">
 @import './styles/index.scss'; 
</style>
