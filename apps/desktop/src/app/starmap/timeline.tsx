import { useRef } from 'react'

import { Codicon } from '@/components/ui/codicon'

import type { TimeAxis } from './time-axis'

interface TimelineProps {
  axis: TimeAxis
  onScrub: (reveal: number) => void
  onTogglePlay: () => void
  playing: boolean
  reveal: number
  // Reveal positions (0–1) where rings spawn — drawn as markers for timing.
  ringStops?: number[]
}

// Compact playback scrubber: a SoundCloud-style waveform — vertical bars
// mirrored around the centre line, height ∝ events per time slice. The played
// (reached) side burns bright, the rest stays muted. Pure presentation — the
// reveal state + rAF sweep live in the StarMap.
export function Timeline({ axis, onScrub, onTogglePlay, playing, reveal, ringStops = [] }: TimelineProps) {
  const trackRef = useRef<HTMLDivElement | null>(null)
  const draggingRef = useRef(false)

  const ratioAt = (clientX: number): number => {
    const rect = trackRef.current?.getBoundingClientRect()

    if (!rect || rect.width === 0) {
      return reveal
    }

    return Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
  }

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    draggingRef.current = true
    e.currentTarget.setPointerCapture(e.pointerId)
    onScrub(ratioAt(e.clientX))
  }

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (draggingRef.current) {
      onScrub(ratioAt(e.clientX))
    }
  }

  const onPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    draggingRef.current = false

    if (e.currentTarget.hasPointerCapture(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId)
    }
  }

  const n = axis.buckets.length

  return (
    <div className="pointer-events-auto flex w-[28rem] max-w-full items-center gap-3 [-webkit-app-region:no-drag]">
      <button
        aria-label={playing ? 'Pause' : 'Play timeline'}
        className="flex size-5 shrink-0 items-center justify-center text-foreground/75 transition-colors hover:text-foreground"
        onClick={onTogglePlay}
        type="button"
      >
        <Codicon name={playing ? 'debug-pause' : 'triangle-right'} size={playing ? '0.8rem' : '0.95rem'} />
      </button>

      <div
        aria-label="Timeline scrubber"
        aria-valuemax={100}
        aria-valuemin={0}
        aria-valuenow={Math.round(reveal * 100)}
        className="relative h-7 min-w-0 flex-1 cursor-pointer select-none touch-none"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        ref={trackRef}
        role="slider"
        tabIndex={0}
      >
        {/* Centre-mirrored bars (items-center) → a symmetric waveform. */}
        <div className="flex h-full w-full items-center gap-[1.5px]">
          {axis.buckets.map((b, i) => {
            const active = (i + 0.5) / n <= reveal
            const intensity = axis.maxTotal > 0 ? b.total / axis.maxTotal : 0
            // Min stub so quiet slices still draw a faint centre tick.
            const heightPct = 12 + intensity * 88

            return (
              <div
                className={`min-w-px flex-1 rounded-full ${active ? 'bg-[var(--theme-primary)]' : 'bg-foreground/20'}`}
                key={i}
                style={{ height: `${heightPct}%`, opacity: active ? 0.55 + 0.45 * intensity : 0.5 }}
              />
            )
          })}
        </div>

        {/* Ring-spawn markers — a dot at each reveal where a ring pops in. */}
        {ringStops.map((stop, i) => (
          <div
            aria-hidden
            className={`pointer-events-none absolute top-1/2 size-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full ${stop <= reveal ? 'bg-[var(--theme-primary)]' : 'bg-foreground/40'}`}
            key={i}
            style={{ left: `${stop * 100}%` }}
          />
        ))}

        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 w-0.5 -translate-x-1/2 rounded-full bg-foreground/90"
          style={{ left: `${reveal * 100}%` }}
        />
      </div>
    </div>
  )
}
