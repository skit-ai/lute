document.addEventListener('DOMContentLoaded', function () {
  d3.json('/data.json').then(data => {
    let g = new dagreD3.graphlib.Graph().setGraph({})

    for (let node of data.nodes) {
      let bg = 'white'
      let fg = '#333'
      if (node.type === 'input') {
        bg = '#333'
        fg = 'white'
      } else if (node.type === 'output') {
        bg = '#008080'
        fg = 'white'
      } else if (node.value !== 'unevaluated') {
        bg = '#ccc'
      }

      let value = {
        rx: 5,
        ry: 5,
        shape: 'rect',
        label: node.name,
        labelStyle: `fill: ${fg}`,
        style: `fill: ${bg}; stroke: ${fg}`,
        description: node.value
      }
      g.setNode(node.name, value)
    }

    for (let edge of data.edges) {
      g.setEdge(edge[0], edge[1], { arrowhead: 'vee' })
    }

    let render = new dagreD3.render()

    let svg = d3.select('svg')
    let inner = svg.append('g')

    let zoom = d3.zoom()
        .on('zoom', function() {
          inner.attr('transform', d3.event.transform)
        })

    render(inner, g)
    svg.call(zoom)

    let { height, width } = svg.node().getBoundingClientRect()
    svg.call(zoom.transform,
             d3.zoomIdentity.translate((width - g.graph().width) / 2, (height - g.graph().height) / 2))

    inner.selectAll('g.node')
      .attr('title', v => g.node(v).description)

    tippy('g.node', { size: 'large' })
  })
})
