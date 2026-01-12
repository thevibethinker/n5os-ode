import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Feed } from '../pages'

export default function Router() {
  return (
    <BrowserRouter>
      <nav style={{ padding: 12, borderBottom: '1px solid #ddd' }}>
        <Link to="/">Home</Link> | <Link to="/feed">Feed</Link>
      </nav>
      <Routes>
        <Route path="/feed" element={<Feed />} />
        <Route path="/" element={<div style={{ padding: 16 }}>ZoBridge Service</div>} />
      </Routes>
    </BrowserRouter>
  )
}
