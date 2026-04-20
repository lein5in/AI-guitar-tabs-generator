import { useState } from 'react'
import ChordDiagram from './ChordDiagram'

interface ChordData {
  name: string
  count: number
  fingers: { s: number; f: number }[]
  muted?: number[]
  open?: number[]
}

// Bibliothèque d'accords communs
const CHORD_LIBRARY: Record<string, Omit<ChordData, 'name' | 'count'>> = {
  'G': {
    fingers: [{ s: 6, f: 3 }, { s: 5, f: 2 }, { s: 2, f: 3 }, { s: 1, f: 3 }],
    open: [4, 3, 2], muted: []
  },
  'D': {
    fingers: [{ s: 3, f: 2 }, { s: 2, f: 3 }, { s: 1, f: 2 }],
    muted: [6, 5], open: [4]
  },
  'C': {
    fingers: [{ s: 5, f: 3 }, { s: 4, f: 2 }, { s: 2, f: 1 }],
    muted: [6], open: [3, 1]
  },
  'Em': {
    fingers: [{ s: 5, f: 2 }, { s: 4, f: 2 }],
    open: [6, 3, 2, 1], muted: []
  },
  'Am': {
    fingers: [{ s: 4, f: 2 }, { s: 3, f: 2 }, { s: 2, f: 1 }],
    muted: [6], open: [5, 1]
  },
  'E': {
    fingers: [{ s: 5, f: 2 }, { s: 4, f: 2 }, { s: 3, f: 1 }],
    open: [6, 2, 1], muted: []
  },
  'A': {
    fingers: [{ s: 4, f: 2 }, { s: 3, f: 2 }, { s: 2, f: 2 }],
    muted: [6], open: [5, 1]
  },
  'Cadd9': {
    fingers: [{ s: 5, f: 3 }, { s: 4, f: 2 }, { s: 2, f: 3 }],
    muted: [6], open: [3, 1]
  },
  'Dsus2': {
    fingers: [{ s: 3, f: 2 }, { s: 2, f: 3 }],
    muted: [6, 5], open: [4, 1]
  },
  'Dm': {
    fingers: [{ s: 3, f: 2 }, { s: 2, f: 3 }, { s: 1, f: 1 }],
    muted: [6, 5], open: [4]
  },
}

interface Props {
  chords: { notes: string[]; index: number }[]
}

export default function ChordsCard({ chords }: Props) {
  const [hoveredChord, setHoveredChord] = useState<string | null>(null)

  // Compter les occurrences de chaque accord
  const chordCounts: Record<string, number> = {}
  chords.forEach(chord => {
    const name = chord.notes[0] ?? 'Unknown'
    chordCounts[name] = (chordCounts[name] ?? 0) + 1
  })

  const uniqueChords = Object.entries(chordCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

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
        Chords — hover to see fingering
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {uniqueChords.map(([name, count]) => {
          const chordData = CHORD_LIBRARY[name]
          const isHovered = hoveredChord === name

          return (
            <div
              key={name}
              style={{ position: 'relative' }}
              onMouseEnter={() => setHoveredChord(name)}
              onMouseLeave={() => setHoveredChord(null)}
            >
              {/* Popup diagramme */}
              {isHovered && chordData && (
                <div style={{
                  position: 'absolute',
                  bottom: 'calc(100% + 10px)',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'rgba(255,252,247,0.97)',
                  border: '0.5px solid rgba(200,118,42,0.3)',
                  borderRadius: 12,
                  padding: '12px 14px 10px',
                  zIndex: 100,
                  boxShadow: '0 8px 32px rgba(42,26,8,0.15)',
                  textAlign: 'center',
                  pointerEvents: 'none',
                }}>
                  <div style={{
                    fontSize: 14, fontWeight: 500, color: '#2a1a08', marginBottom: 8,
                  }}>
                    {name}
                  </div>
                  <ChordDiagram
                    name={name}
                    fingers={chordData.fingers}
                    muted={chordData.muted}
                    open={chordData.open}
                  />
                  {/* Flèche */}
                  <div style={{
                    position: 'absolute',
                    top: '100%', left: '50%',
                    transform: 'translateX(-50%)',
                    width: 0, height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderTop: '6px solid rgba(200,118,42,0.3)',
                  }} />
                </div>
              )}

              {/* Chip */}
              <div style={{
                background: isHovered ? 'rgba(200,118,42,0.2)' : 'rgba(200,118,42,0.1)',
                border: `0.5px solid ${isHovered ? 'rgba(200,118,42,0.5)' : 'rgba(200,118,42,0.25)'}`,
                borderRadius: 8, padding: '6px 12px',
                fontSize: 13, color: 'rgba(42,26,8,0.7)',
                display: 'flex', alignItems: 'baseline', gap: 5,
                cursor: 'pointer', transition: 'all 0.15s',
                userSelect: 'none',
              }}>
                {name}
                <span style={{ fontSize: 11, color: 'rgba(200,118,42,0.55)' }}>
                  ×{count}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}