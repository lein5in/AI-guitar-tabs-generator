import { useState } from 'react'
import UploadZone from '../components/UploadZone'
import StatsRow from '../components/StatsRow'
import TabDisplay from '../components/TabDisplay'
import TuningCard from '../components/TuningCard'
import ChordsCard from '../components/ChordsCard'
import { transcribeAudio } from '../api/fretify'
import type { TranscribeResponse, AppState } from '../types'

export default function Home() {
  const [state, setState] = useState<AppState>('idle')
  const [result, setResult] = useState<TranscribeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = async (file: File) => {
    setState('loading')
    setError(null)
    setResult(null)

    try {
      const data = await transcribeAudio(file)
      setResult(data)
      console.log('Chords:', data.chords)
      setState('results')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Transcription failed'
      setError(message)
      setState('error')
    }
  }

  return (
    <div>
      {/* Animated background orbs */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', width: 500, height: 500,
          background: '#e8a045', borderRadius: '50%',
          filter: 'blur(80px)', opacity: 0.45,
          top: -150, left: -100,
          animation: 'drift1 12s ease-in-out infinite alternate',
        }} />
        <div style={{
          position: 'absolute', width: 400, height: 400,
          background: '#d4623a', borderRadius: '50%',
          filter: 'blur(80px)', opacity: 0.35,
          top: 200, right: -120,
          animation: 'drift2 14s ease-in-out infinite alternate',
        }} />
        <div style={{
          position: 'absolute', width: 350, height: 350,
          background: '#c8762a', borderRadius: '50%',
          filter: 'blur(80px)', opacity: 0.3,
          bottom: -100, left: '30%',
          animation: 'drift3 10s ease-in-out infinite alternate',
        }} />
      </div>

      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Hero */}
        <div style={{ padding: '56px 32px 36px', textAlign: 'center' }}>
          <h1 style={{
            fontSize: 44, fontWeight: 500,
            letterSpacing: -1.2, lineHeight: 1.1,
            marginBottom: 12, color: '#2a1a08',
          }}>
            Your guitar,{' '}
            <em style={{ fontStyle: 'normal', color: '#c8762a' }}>transcribed.</em>
          </h1>
          <p style={{
            fontSize: 16, color: 'rgba(42,26,8,0.45)',
            marginBottom: 36, maxWidth: 400,
            marginLeft: 'auto', marginRight: 'auto', lineHeight: 1.6,
          }}>
            Drop any video or recording — Fretify turns it into playable tabs in seconds.
          </p>

          <UploadZone
            onFileSelect={handleFileSelect}
            loading={state === 'loading'}
          />
        </div>

        {/* Error */}
        {state === 'error' && error && (
          <div style={{
            maxWidth: 520, margin: '0 auto 32px',
            background: 'rgba(255,100,50,0.1)',
            border: '0.5px solid rgba(255,100,50,0.3)',
            borderRadius: 12, padding: '16px 20px',
            fontSize: 14, color: '#a83010', textAlign: 'center',
          }}>
            {error}
          </div>
        )}

        {/* Results */}
        {state === 'results' && result && (
          <>
            {/* Separator */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 16,
              maxWidth: 900, margin: '0 auto 20px', padding: '0 32px',
            }}>
              <div style={{ flex: 1, height: '0.5px', background: 'rgba(200,118,42,0.2)' }} />
              <span style={{ fontSize: 11, color: 'rgba(200,118,42,0.6)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Results
              </span>
              <div style={{ flex: 1, height: '0.5px', background: 'rgba(200,118,42,0.2)' }} />
            </div>

            <div style={{
              maxWidth: 900, margin: '0 auto',
              padding: '0 32px 52px',
              display: 'flex', flexDirection: 'column', gap: 16,
            }}>
              <StatsRow stats={result.stats} duration={result.duration} />

              <TabDisplay
                ascii={result.tablature.ascii}
                capo={result.tuning.capo}
                capoLabel={result.tuning.capo_label}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <TuningCard tuning={result.tuning} />
                <ChordsCard chords={result.chords} />
              </div>
            </div>
          </>
        )}
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes drift1 {
          from { transform: translate(0, 0) scale(1); }
          to   { transform: translate(30px, 20px) scale(1.08); }
        }
        @keyframes drift2 {
          from { transform: translate(0, 0) scale(1); }
          to   { transform: translate(-25px, 30px) scale(1.05); }
        }
        @keyframes drift3 {
          from { transform: translate(0, 0) scale(1); }
          to   { transform: translate(20px, -25px) scale(1.1); }
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}