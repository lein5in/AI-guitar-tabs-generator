import type { TranscribeStats } from '../types'

interface Props {
  stats: TranscribeStats
  duration: number
}

function StatCard({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.6)',
      backdropFilter: 'blur(8px)',
      border: '0.5px solid rgba(200,118,42,0.2)',
      borderRadius: 14,
      padding: '16px 18px',
    }}>
      <div style={{ fontSize: 11, color: 'rgba(42,26,8,0.35)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 30, fontWeight: 500, color: '#2a1a08', letterSpacing: -0.5, lineHeight: 1, marginBottom: 4 }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: '#c8762a' }}>{sub}</div>
    </div>
  )
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function StatsRow({ stats, duration }: Props) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 10,
    }}>
      <StatCard label="Notes" value={String(stats.total_notes_detected)} sub="detected" />
      <StatCard label="Tab positions" value={String(stats.tab_positions)} sub="generated" />
      <StatCard label="Chords" value={String(stats.chords_detected)} sub="identified" />
      <StatCard label="Duration" value={formatDuration(duration)} sub="audio length" />
    </div>
  )
}