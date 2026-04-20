import type { TuningResult } from '../types'

interface Props {
  tuning: TuningResult
}

export default function TuningCard({ tuning }: Props) {
  const stringNames = ['6', '5', '4', '3', '2', '1']

  return (
    <div style={{
      background: 'rgba(255,255,255,0.55)',
      backdropFilter: 'blur(8px)',
      border: '0.5px solid rgba(200,118,42,0.18)',
      borderRadius: 14,
      padding: '18px 20px',
    }}>
      <div style={{
        fontSize: 11, color: 'rgba(42,26,8,0.3)',
        textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 14,
      }}>
        Tuning detected
      </div>

      {/* Cordes */}
      <div style={{ display: 'flex', gap: 7 }}>
        {tuning.notes.map((note, i) => (
          <div key={i} style={{
            background: 'rgba(200,118,42,0.08)',
            border: '0.5px solid rgba(200,118,42,0.2)',
            borderRadius: 8, padding: '8px 11px',
            textAlign: 'center', flex: 1,
          }}>
            <div style={{ fontSize: 10, color: 'rgba(42,26,8,0.3)', marginBottom: 3 }}>
              {stringNames[i]}
            </div>
            <div style={{ fontSize: 15, fontWeight: 500, color: '#c8762a' }}>
              {note.replace(/\d/, '')}
            </div>
          </div>
        ))}
      </div>

      {/* Tuning name + confidence */}
      <div style={{ marginTop: 12, fontSize: 13, color: 'rgba(42,26,8,0.4)' }}>
        {tuning.detected.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        &nbsp;·&nbsp;
        <span style={{ color: '#c8762a' }}>
          {Math.round(tuning.confidence * 100)}% confidence
        </span>
      </div>

      {/* Capo si détecté */}
      {tuning.capo > 0 && (
        <div style={{
          marginTop: 10,
          display: 'inline-block',
          background: 'rgba(200,118,42,0.15)',
          color: '#a85a10',
          border: '0.5px solid rgba(200,118,42,0.3)',
          borderRadius: 6, fontSize: 12, padding: '4px 10px',
        }}>
          {tuning.capo_label}
        </div>
      )}
    </div>
  )
}