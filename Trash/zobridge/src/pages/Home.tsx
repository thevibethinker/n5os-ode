import { Link } from 'react-router-dom'
export default function Home(){
  return (
    <div style={{padding:16}}>
      <h2>ZoBridge Service</h2>
      <p><Link to="/feed">Open Live Feed</Link></p>
    </div>
  )
}
