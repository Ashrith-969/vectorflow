import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import AskPage from './pages/AskPage';
import SearchPage from './pages/SearchPage';
import IngestPage from './pages/IngestPage';
import BulkIngestPage from './pages/BulkIngestPage';
import AdminPage from './pages/AdminPage';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/ask" element={
        <ProtectedRoute>
          <Layout><AskPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/search" element={
        <ProtectedRoute>
          <Layout><SearchPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/ingest" element={
        <ProtectedRoute roles={['EDITOR', 'ADMIN']}>
          <Layout><IngestPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/bulk-ingest" element={
        <ProtectedRoute roles={['EDITOR', 'ADMIN']}>
          <Layout><BulkIngestPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute roles={['ADMIN']}>
          <Layout><AdminPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/ask" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
