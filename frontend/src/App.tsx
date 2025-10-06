import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Placement from './pages/Placement'
import Search from './pages/Search'
import Waste from './pages/Waste'
import Simulation from './pages/Simulation'
import ImportExport from './pages/ImportExport'
import Logs from './pages/Logs'
import Visualization from './pages/Visualization'
import Inventory from './pages/Inventory'
import Emergency from './pages/Emergency'

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/placement" element={<Placement />} />
            <Route path="/search" element={<Search />} />
            <Route path="/waste" element={<Waste />} />
            <Route path="/simulation" element={<Simulation />} />
            <Route path="/import-export" element={<ImportExport />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/visualization" element={<Visualization />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/emergency" element={<Emergency />} />
          </Routes>
        </Layout>
      </Box>
    </Router>
  )
}

export default App
