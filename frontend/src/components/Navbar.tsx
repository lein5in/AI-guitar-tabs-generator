export default function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      background: 'rgba(245,237,224,0.7)',
      backdropFilter: 'blur(12px)',
      borderBottom: '0.5px solid rgba(180,120,50,0.15)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 34, height: 34,
          background: '#c8762a',
          borderRadius: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="white" strokeWidth="2.2" strokeLinecap="round">
            <path d="M9 18V5l12-2v13"/>
            <circle cx="6" cy="18" r="3"/>
            <circle cx="18" cy="16" r="3"/>
          </svg>
        </div>
        <span style={{ fontSize: 20, fontWeight: 500, color: '#2a1a08', letterSpacing: -0.3 }}>
          Fretify
        </span>
      </div>
      <div style={{ display: 'flex', gap: 24, fontSize: 14, color: 'rgba(42,26,8,0.4)' }}>
        <span style={{ cursor: 'pointer' }}>My tabs</span>
        <span style={{ cursor: 'pointer' }}>Tunings</span>
        <span style={{ cursor: 'pointer' }}>About</span>
      </div>
    </nav>
  )
}