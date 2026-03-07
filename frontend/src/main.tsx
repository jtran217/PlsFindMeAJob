import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import ProfilePage from './pages/ProfilePage'
import EnhancedProfilePage from './pages/EnhancedProfilePage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/resume" element={<EnhancedProfilePage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
