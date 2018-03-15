<template lang="pug">
  section.rps-input
    .buttons.has-addons.is-centered
      button.button.is-medium(@click='onClick("r")', :disabled="disabled")
        span.icon: font-awesome-icon(icon='hand-rock')
        span Rock

      button.button.is-medium(@click='onClick("p")', :disabled="disabled")
        span.icon: font-awesome-icon(icon='hand-paper')
        span Paper

      button.button.is-medium(@click='onClick("s")', :disabled="disabled")
        span.icon
          font-awesome-icon(icon='hand-scissors')
        span Scissors
</template>

<script lang="js">
export default {
  name: 'rps-input',
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
    }
  },
  methods: {
    onClick (e) {
      this.$emit('choice', e)
    }
  }
}
</script>

<style scoped lang="stylus">
</style>
