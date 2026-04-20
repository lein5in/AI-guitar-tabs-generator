import Navbar from './components/Navbar'
import Home from './pages/Home'

export default function App() {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#f5ede0',
      fontFamily: 'sans-serif',
    }}>
      <Navbar />
      <Home />
    </div>
  )
}