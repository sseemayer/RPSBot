<template lang="pug">

  #app
    nav.navbar.is-primary(role='navigation',aria-label='main navigation')
      .navbar-brand
        a.navbar-item(href='/') RPSBot

    section.section.main
      .enter(v-if='mode==="input"')
        p.is-size-1.has-text-centered Choose your move!
        RPSInput(@choice='onPlayerChoice', :disabled="!botChoice")

      .output(v-if='mode==="result"')
        .box.result
          .columns
            .column
              p.is-size-2 You chose
              font-awesome-icon.is-size-2.has-text-info(:icon='choiceToIcon(playerChoice)')
            .column
              p.is-size-2 Bot chose
              font-awesome-icon.is-size-2.has-text-info(:icon='choiceToIcon(botChoice)')

          p.is-size-1.winner {{winner}}

        .box
          h4.is-size-4 Predictions
          .columns.has-text-centered
            .column(:class='{"has-text-primary": playerChoice === "r"}')
              font-awesome-icon(icon='hand-rock')
              div {{(botProbs.r * 100).toFixed(0)}}%

            .column(:class='{"has-text-primary": playerChoice === "p"}')
              font-awesome-icon(icon='hand-paper')
              div {{(botProbs.p * 100).toFixed(0)}}%

            .column(:class='{"has-text-primary": playerChoice === "s"}')
              font-awesome-icon(icon='hand-scissors')
              div {{(botProbs.s * 100).toFixed(0)}}%

        .container.buttonbox
          button.button.is-primary.is-medium(@click='onConfirmResult')
            span.icon: font-awesome-icon(icon='sync')
            span Next round

      .stats.box
        h4.is-size-4 Total wins
        .columns.has-text-centered
          .column
            font-awesome-icon(icon='smile')
            div {{playerWins}}

          .column
            font-awesome-icon(icon='desktop')
            div {{botWins}}

          .column
            font-awesome-icon(icon='balance-scale')
            div {{draws}}


        .plot(ref='plot')

    section.has-text-centered
      a(@click='onReset') Forget what you've learned
</template>

<script>
import '../node_modules/@fortawesome/fontawesome/index.js'
import RPSInput from './components/RPSInput.vue'
import axios from 'axios'
import * as d3 from 'd3'

const apiURL = '/api'

function score (p, b) {
  if (p === b) {
    return 'd'
  } else if (p === 'r' && b === 'p') {
    return 'b'
  } else if (p === 'r' && b === 's') {
    return 'p'
  } else if (p === 'p' && b === 'r') {
    return 'p'
  } else if (p === 'p' && b === 's') {
    return 'b'
  } else if (p === 's' && b === 'r') {
    return 'b'
  } else if (p === 's' && b === 'p') {
    return 'p'
  } else {
    throw Error('Unknown choices: ' + p + b)
  }
}

export default {
  name: 'App',
  data () {
    this.requestPrediction()

    let dimensions = {
      width: 800,
      height: 300
    }

    let margin = {
      left: 60,
      top: 10,
      right: 10,
      bottom: 10
    }

    let x = d3.scaleLinear()
      .domain([0, 1])
      .range([0, dimensions.width - margin.left - margin.right])

    let y = d3.scaleLinear()
      .domain([-1, 1])
      .range([0, dimensions.height - margin.top - margin.bottom])

    return {
      playerWins: 0,
      botWins: 0,
      draws: 0,
      mode: 'input',

      playerChoice: null,
      botChoice: null,
      winner: null,

      botProbs: null,

      history: [{playerWins: 0, botWins: 0, draws: 0}],

      dimensions: dimensions,
      margin: margin,

      plotContainer: null,
      svg: null,
      main: null,
      line: d3.line()
        .x((d, i) => this.x(i))
        .y((d) => this.y(d.playerWins - d.botWins)),

      baseLine: null,

      path: null,
      x: x,
      y: y,

      yAxis: d3.axisLeft(y),
      gYAxis: null
    }
  },

  mounted () {
    window.addEventListener('resize', this.redraw.bind(this))

    this.plotContainer = this.$refs.plot

    this.dimensions.width = this.plotContainer.clientWidth

    this.svg = d3.select(this.plotContainer).append('svg')
      .attr('width', this.dimensions.width)
      .attr('height', this.dimensions.height)

    this.main = this.svg.append('g')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)

    this.baseLine = this.main.append('path')
      .attr('class', 'base-line')
      .attr('d', `M ${this.x(0)} ${this.y(0)} L ${this.dimensions.width - this.margin.left - this.margin.right} ${this.y(0)}`)

    this.path = this.main.append('path')
      .attr('class', 'data')

    this.main.append('text')
      .attr('class', 'legend')
      .attr('x', -75)
      .attr('y', -40)
      .attr('transform', 'rotate(-90)')
      .text('Bot better')

    this.main.append('text')
      .attr('class', 'legend')
      .attr('x', -225)
      .attr('y', -40)
      .attr('transform', 'rotate(-90)')
      .text('Player better')

    this.gYAxis = this.main.append('g')
      .attr('class', 'y axis')

    this.redraw()
  },

  components: {
    RPSInput
  },

  methods: {
    redraw () {
      this.dimensions.width = this.plotContainer.clientWidth
      this.svg.attr('width', this.dimensions.width)
      this.x.range([0, this.dimensions.width - this.margin.left - this.margin.right])

      let extent = d3.max(this.history, (d) => Math.abs(d.playerWins - d.botWins)) + 0.1

      this.x.domain([0, this.history.length - 1])
      this.y.domain([-extent, extent])

      this.gYAxis.call(this.yAxis)
      this.baseLine.attr('d', `M ${this.x(0)} ${this.y(0)} L ${this.dimensions.width - this.margin.left - this.margin.right} ${this.y(0)}`)

      this.path.datum(this.history)
        .attr('d', this.line)
    },

    requestPrediction () {
      this.botChoice = null

      axios.get(apiURL + '/predict', {withCredentials: true})
        .then((r) => {
          this.botChoice = r.data.best_strategy
          this.botProbs = r.data.predicted_plays
          console.log(`bot will choose ${r.data.best_strategy} with expected outcome of ${r.data.expected_outcome}`)
        })
    },

    choiceToIcon (c) {
      return {
        'r': 'hand-rock',
        'p': 'hand-paper',
        's': 'hand-scissors'
      }[c]
    },

    onPlayerChoice (c) {
      this.playerChoice = c

      axios.post(apiURL + '/event', 'event=' + c + this.botChoice, {withCredentials: true})

      let outcome = score(this.playerChoice, this.botChoice)
      if (outcome === 'd') {
        this.winner = "It's a draw!"
        this.draws = this.draws + 1
      } else if (outcome === 'p') {
        this.winner = 'You win!'
        this.playerWins = this.playerWins + 1
      } else if (outcome === 'b') {
        this.winner = 'Bot wins!'
        this.botWins = this.botWins + 1
      } else {
        this.winner = 'what happened?'
      }

      this.history.push({
        'playerWins': this.playerWins,
        'botWins': this.botWins,
        'draws': this.draws
      })

      this.redraw()

      this.mode = 'result'
      console.log('player chose', c)
    },

    onConfirmResult () {
      this.mode = 'input'

      this.playerChoice = null
      this.requestPrediction()
    },

    onReset () {
      this.botChoice = null
      this.botWins = 0
      this.playerWins = 0
      this.mode = 'input'
      this.history = [{playerWins: 0, botWins: 0, draws: 0}]

      this.redraw()

      axios.post(apiURL + '/reset', {}, {withCredentials: true})
        .then(() => this.requestPrediction())
    }
  }
}
</script>

<style lang="scss">
@import '../node_modules/bulma/bulma.sass';

.result svg {
  margin: 0 auto;
  display: block;
}

.result p {
  text-align: center;
}

dt, dd {
  display: inline-block;
}

dt {
  padding-right: 5pt;
}

dd {
  width: 100pt;
}

.main, .plot {
  max-width: 800px;
  margin: 0 auto;
}

.plot svg path {
  fill: none;
}

.plot svg path.data {
  stroke: hsl(48, 100%, 67%);
  stroke-width: 3px;
}

.plot svg path.base-line {
  stroke: #ccc;
  stroke-width: 3px;
  stroke-dasharray: 5,5;
}

.plot text.legend {
  text-anchor: middle;
}

.buttonbox, .stats {
  margin: 20px 0;
}
</style>
