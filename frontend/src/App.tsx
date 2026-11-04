import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"
import { Login } from "@/pages/Login"
import { Dashboard } from "@/pages/Dashboard"
import { RepoAnalytics } from "@/pages/RepoAnalytics"

export default function App() {
  const { user, loading } = useAuth()

  // While the session cookie is being validated, render nothing so the
  // router doesn't flash the wrong route before auth resolves.
  if (loading) return null

  return (
    <BrowserRouter>
      <Routes>
        {user ? (
          <>
            <Route path="/" element={<Dashboard />} />
            <Route path="/repositories/:id" element={<RepoAnalytics />} />
            <Route path="/login" element={<Navigate to="/" replace />} />
          </>
        ) : (
          <>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  )
}
