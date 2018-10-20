/* global d3 tippy dagreD3 data */

function simplifyName (nodeName) {
  let brk = nodeName.indexOf('__')
  if (brk > -1) {
    return nodeName.slice(0, brk + 10) + '...'
  } else {
    return nodeName
  }
}

function clipDescription (nodeDesc) {
  let maxlen = 500
  return nodeDesc.slice(0, maxlen)
}

document.addEventListener('DOMContentLoaded', function () {
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
      label: simplifyName(node.name),
      labelStyle: `fill: ${fg}`,
      style: `fill: ${bg}; stroke: ${fg}`,
      description: '<pre>' + JSON.stringify(node.value, null, 2) + '</pre>'
    }
    g.setNode(node.name, value)
  }

  for (let edge of data.edges) {
    g.setEdge(edge[0], edge[1], { arrowhead: 'vee' })
  }

  let render = new dagreD3.render()

  let svg = d3.select('svg')
  let inner = svg.append('g')

  let zoom = d3.zoom().on('zoom', function () {
    inner.attr('transform', d3.event.transform)
  })

  render(inner, g)
  svg.call(zoom)

  let { height, width } = svg.node().getBoundingClientRect()
  svg.call(zoom.transform, d3.zoomIdentity.translate((width - g.graph().width) / 2, (height - g.graph().height) / 2))

  inner.selectAll('g.node')
    .attr('title', v => clipDescription(g.node(v).description))
  let first = true
  inner.selectAll('g.node')
    .on('click', function (v) {
      let node = g.node(v)
      if (first) {
        first = false
        d3.select('.desc').append("pre").html(node.description)
      } else {
        d3.select('.desc').select("pre").html(node.description)
      }
      d3.select('.title').text(node.label)
    })

  tippy('g.node', { size: 'large' })
})
