interface Finger {
  s: number  // string 1-6
  f: number  // fret
}

interface Props {
  name: string
  fingers: Finger[]
  muted?: number[]
  open?: number[]
}

export default function ChordDiagram({ name, fingers, muted = [], open = [] }: Props) {
  const W = 110, H = 115
  const ml = 18, mt = 24, mr = 10
  const cols = 6, rows = 4
  const cw = (W - ml - mr) / (cols - 1)
  const rh = (H - mt - 20) / rows

  const frets = fingers.map(f => f.f).filter(f => f > 0)
  const minFret = frets.length ? Math.min(...frets) : 1
  const startFret = minFret > 1 ? minFret : 1

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {/* Nut ou numéro de frette */}
      {startFret === 1 ? (
        <rect x={ml} y={mt - 5} width={(cols - 1) * cw} height={4} fill="#2a1a08" rx={1} />
      ) : (
        <text x={ml - 6} y={mt + rh * 0.5} fontSize={9} fill="#c8762a"
          textAnchor="end" fontFamily="sans-serif">
          {startFret}
        </text>
      )}

      {/* Lignes horizontales (frettes) */}
      {Array.from({ length: rows + 1 }, (_, r) => (
        <line key={r}
          x1={ml} y1={mt + r * rh}
          x2={ml + (cols - 1) * cw} y2={mt + r * rh}
          stroke="#2a1a08" strokeWidth={0.5} strokeOpacity={0.3}
        />
      ))}

      {/* Lignes verticales (cordes) */}
      {Array.from({ length: cols }, (_, c) => (
        <line key={c}
          x1={ml + c * cw} y1={mt}
          x2={ml + c * cw} y2={mt + rows * rh}
          stroke="#2a1a08" strokeWidth={0.5} strokeOpacity={0.35}
        />
      ))}

      {/* Muted / Open au-dessus */}
      {Array.from({ length: cols }, (_, c) => {
        const stringNum = cols - c  // 6 à 1
        const x = ml + c * cw
        const y = mt - 11
        if (muted.includes(stringNum)) {
          return (
            <text key={c} x={x} y={y} fontSize={10} fill="#2a1a08"
              textAnchor="middle" fontFamily="sans-serif" opacity={0.5}>
              ×
            </text>
          )
        }
        if (open.includes(stringNum)) {
          return (
            <circle key={c} cx={x} cy={y - 1} r={4}
              fill="none" stroke="#2a1a08" strokeWidth={1} opacity={0.45}
            />
          )
        }
        return null
      })}

      {/* Points des doigts */}
      {fingers.map((finger, i) => {
        if (finger.f === 0) return null
        const col = cols - 1 - (finger.s - 1)
        const row = finger.f - startFret + 1
        if (row < 1 || row > rows) return null
        const x = ml + col * cw
        const y = mt + (row - 0.5) * rh
        return (
          <circle key={i} cx={x} cy={y} r={7} fill="#c8762a" />
        )
      })}
    </svg>
  )
}