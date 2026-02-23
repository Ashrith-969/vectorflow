import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { MessageSquare, Search, Upload, Files, Users, LogOut, Zap } from 'lucide-react';
import RoleBadge from './RoleBadge';

const navItems = [
  { to: '/ask', icon: MessageSquare, label: 'Ask AI', roles: ['VIEWER', 'EDITOR', 'ADMIN'] },
  { to: '/search', icon: Search, label: 'Search', roles: ['VIEWER', 'EDITOR', 'ADMIN'] },
  { to: '/ingest', icon: Upload, label: 'Ingest', roles: ['EDITOR', 'ADMIN'] },
  { to: '/bulk-ingest', icon: Files, label: 'Bulk Ingest', roles: ['EDITOR', 'ADMIN'] },
  { to: '/admin', icon: Users, label: 'Users', roles: ['ADMIN'] },
];

export default function Layout({ children }) {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleItems = navItems.filter(item =>
    item.roles.some(role => hasRole(role))
  );

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white flex flex-col flex-shrink-0">
        <div className="p-5 border-b border-gray-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Zap size={20} />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight">VectorFlow</h1>
              <p className="text-[11px] text-gray-400 leading-tight">RAG Search Engine</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1">
          {visibleItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-400 border-l-2 border-indigo-400 -ml-[2px] pl-[14px]'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-gray-700 rounded-full flex items-center justify-center text-sm font-bold">
              {user?.email?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.email}</p>
              <RoleBadge role={user?.role} size="sm" />
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-gray-400 hover:text-white text-sm w-full px-2 py-1.5 rounded transition-colors hover:bg-gray-800"
          >
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-gray-50">
        {children}
      </main>
    </div>
  );
}
