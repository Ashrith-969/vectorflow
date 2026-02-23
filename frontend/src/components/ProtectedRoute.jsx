import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert } from 'lucide-react';

export default function ProtectedRoute({ children, roles }) {
  const { user, hasRole } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.some(r => hasRole(r))) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <ShieldAlert size={48} className="mx-auto text-red-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-500">You don't have permission to view this page.</p>
        </div>
      </div>
    );
  }

  return children;
}
