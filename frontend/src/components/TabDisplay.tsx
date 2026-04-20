interface Props {
  ascii: string
  capoLabel: string
  capo: number
}

export default function TabDisplay({ ascii, capoLabel, capo }: Props) {
  const handleCopy = () => {
    navigator.clipboard.writeText(ascii)
  }

  const lines = ascii.split('\n')

  return (
    <div style={{
      background: 'rgba(255,255,255,0.55)',
      backdropFilter: 'blur(8px)',
      border: '0.5px solid rgba(200,118,42,0.2)',
      borderRadius: 16,
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 20px',
        borderBottom: '0.5px solid rgba(200,118,42,0.12)',
        background: 'rgba(200,118,42,0.06)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 500, color: 'rgba(42,26,8,0.6)' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="3" width="20" height="14" rx="2"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
          </svg>
          Tablature
          {capo > 0 && (
            <span style={{
              background: 'rgba(200,118,42,0.15)', color: '#a85a10',
              border: '0.5px solid rgba(200,118,42,0.3)',
              borderRadius: 6, fontSize: 11, padding: '3px 8px',
            }}>
              {capoLabel}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={handleCopy} style={{
            padding: '7px 14px', borderRadius: 8,
            border: '0.5px solid rgba(200,118,42,0.3)',
            background: 'rgba(200,118,42,0.08)',
            color: 'rgba(42,26,8,0.5)', cursor: 'pointer',
            fontSize: 12, fontFamily: 'inherit',
          }}>
            Copy
          </button>
        </div>
      </div>

      {/* Tab lines */}
      <div style={{ padding: '22px 20px', overflowX: 'auto' }}>
        {lines.map((line, i) => {
          const stringName = line[0]
          const rest = line.slice(1)
          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center',
              fontFamily: 'var(--font-mono, monospace)',
              fontSize: 13, lineHeight: '2.1',
              whiteSpace: 'nowrap',
            }}>
              <span style={{ color: '#c8762a', fontWeight: 500, minWidth: 20 }}>
                {stringName}
              </span>
              <span style={{ color: 'rgba(42,26,8,0.65)' }}>{rest}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}