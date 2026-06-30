import { forceCollide, forceLink, forceManyBody, forceRadial, forceSimulation, type Simulation } from 'd3-force'

import type { StarmapGraph } from '@/types/hermes'

import { RING_STEPS } from './constants'
import { hash, nodeRadius, radiusForRecency } from './geometry'
import { formatDate } from './text'
import { computeRecency, recForRatio } from './time-axis'
import type { Ring, SimLink, SimNode } from './types'

export interface BuiltSim {
  byId: Map<string, SimNode>
  links: SimLink[]
  nodes: SimNode[]
  rings: Ring[]
  sim: Simulation<SimNode, SimLink>
}

// Build the radial time simulation: a node's distance from the core encodes its
// timestamp (radial force dominates; charge/collide only spread nodes around
// their date ring). Rings are dated gridlines across the time span.
export function buildSimulation(graph: StarmapGraph, onTick: () => void): BuiltSim {
  const { maxTs, minTs, rec: recById, timed } = computeRecency(graph.nodes)

  const nodes: SimNode[] = graph.nodes.map(n => {
    const rec = recById.get(n.id) ?? 0
    const tr = radiusForRecency(rec)
    const angle = ((hash(n.id) % 3600) / 3600) * Math.PI * 2

    return { ...n, rec, tr, vx: 0, vy: 0, x: Math.cos(angle) * tr, y: Math.sin(angle) * tr }
  })

  const byId = new Map(nodes.map(n => [n.id, n]))

  const links: SimLink[] = graph.edges
    .filter(e => byId.has(e.source) && byId.has(e.target))
    .map(e => ({ source: e.source, target: e.target }))

  const sim = forceSimulation(nodes)
    .alphaDecay(0.05)
    .velocityDecay(0.62)
    .force('charge', forceManyBody<SimNode>().strength(-12))
    .force(
      'link',
      forceLink<SimNode, SimLink>(links)
        .id(n => n.id)
        .distance(26)
        .strength(0.06)
    )
    .force(
      'collide',
      forceCollide<SimNode>()
        .radius(n => nodeRadius(n) + 2)
        .iterations(2)
    )
    .force('radial', forceRadial<SimNode>(n => (n as SimNode).tr, 0, 0).strength(0.92))
    .on('tick', onTick)

  const rings: Ring[] = []

  for (let i = 0; i <= RING_STEPS; i += 1) {
    const frac = i / RING_STEPS
    // Rings live in the SAME lead-in space as node recency, so a node dated F
    // sits exactly on the ring dated F (and timeline ring-markers line up with
    // the node bars). The date label still reflects the raw time fraction.
    const ratio = recForRatio(frac)
    const r = radiusForRecency(ratio)
    const label = i > 0 && timed && minTs !== null && maxTs !== null ? formatDate(Math.round(minTs + (maxTs - minTs) * frac)) : null

    rings.push({ label, r, ratio })
  }

  return { byId, links, nodes, rings, sim }
}
