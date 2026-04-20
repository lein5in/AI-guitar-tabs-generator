import { useRef, useState } from 'react'

interface Props {
  onFileSelect: (file: File) => void
  loading: boolean
}

export default function UploadZone({ onFileSelect, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = (file: File) => {
    if (loading) return
    onFileSelect(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onClick={() => !loading && inputRef.current?.click()}
      style={{
        margin: '0 auto 52px',
        maxWidth: 520,
        background: dragging ? 'rgba(255,255,255,0.75)' : 'rgba(255,255,255,0.55)',
        backdropFilter: 'blur(10px)',
        border: `1.5px dashed ${dragging ? 'rgba(200,118,42,0.75)' : 'rgba(200,118,42,0.45)'}`,
        borderRadius: 20,
        padding: '36px 28px',
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        gap: 12,
        cursor: loading ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s',
        opacity: loading ? 0.6 : 1,
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".mp3,.wav,.flac,.ogg,.m4a,.mp4,.mov,.avi,.mkv,.webm"
        style={{ display: 'none' }}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFile(file)
        }}
      />

      <div style={{
        width: 54, height: 54,
        background: 'rgba(200,118,42,0.12)',
        borderRadius: 16,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {loading ? (
            <div style={{
            width: 26, height: 26,
            border: '2.5px solid rgba(200,118,42,0.2)',
            borderTop: '2.5px solid #c8762a',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
        }} />
        ) : (
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
            stroke="#c8762a" strokeWidth="1.8" strokeLinecap="round">
            <polyline points="16 16 12 12 8 16"/>
            <line x1="12" y1="12" x2="12" y2="21"/>
            <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
          </svg>
        )}
      </div>

      <p style={{ fontSize: 15, color: 'rgba(42,26,8,0.5)' }}>
        {loading ? 'Transcribing… this can take a few minutes' : 'Drop your video or audio here'}
      </p>
      <small style={{ fontSize: 12, color: 'rgba(42,26,8,0.28)' }}>
        MP4 · MOV · MP3 · WAV · FLAC &nbsp;·&nbsp; max 100 MB
      </small>

      {!loading && (
        <button
          style={{
            background: '#c8762a', color: '#fff',
            border: 'none', borderRadius: 10,
            padding: '10px 26px', fontSize: 14, fontWeight: 500,
            cursor: 'pointer', fontFamily: 'inherit',
          }}
          onClick={(e) => { e.stopPropagation(); inputRef.current?.click() }}
        >
          Choose a file
        </button>
      )}
    </div>
  )
}