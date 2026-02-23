import { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { USERS } from '../graphql/queries';
import { ASSIGN_ROLE } from '../graphql/mutations';
import RoleBadge from '../components/RoleBadge';
import { Loader2, CheckCircle, AlertTriangle } from 'lucide-react';

const ROLES = ['VIEWER', 'EDITOR', 'ADMIN'];

export default function AdminPage() {
  const { data, loading, error, refetch } = useQuery(USERS);
  const [assignRole] = useMutation(ASSIGN_ROLE);
  const [confirm, setConfirm] = useState(null);
  const [assigning, setAssigning] = useState(false);
  const [toast, setToast] = useState(null);

  const handleRoleChange = (user, newRole) => {
    if (user.role === newRole) return;
    setConfirm({ user, newRole });
  };

  const confirmAssign = async () => {
    if (!confirm) return;
    setAssigning(true);
    try {
      await assignRole({
        variables: { input: { userId: confirm.user.id, role: confirm.newRole } },
      });
      setToast({ type: 'success', message: `${confirm.user.email} is now ${confirm.newRole}` });
      refetch();
    } catch (err) {
      setToast({ type: 'error', message: err.message });
    } finally {
      setAssigning(false);
      setConfirm(null);
      setTimeout(() => setToast(null), 4000);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">User Management</h1>
        <p className="text-sm text-gray-500">Manage user roles and permissions</p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          {toast && (
            <div className={`mb-4 p-3 rounded-lg flex items-center gap-2 text-sm ${
              toast.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {toast.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
              {toast.message}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 size={24} className="animate-spin text-indigo-500" />
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg border border-red-100">
              {error.message}
            </div>
          )}

          {data && (
            <div className="card p-0 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">User</th>
                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">Current Role</th>
                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">Joined</th>
                    <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">Change Role</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {data.users.map(user => (
                    <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center text-sm font-bold text-indigo-600">
                            {user.email[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-800">{user.email}</p>
                            <p className="text-xs text-gray-400">{user.id.slice(0, 8)}...</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <RoleBadge role={user.role} />
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(user.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={user.role}
                          onChange={(e) => handleRoleChange(user, e.target.value)}
                          className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                        >
                          {ROLES.map(r => (
                            <option key={r} value={r}>{r}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {confirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setConfirm(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Confirm Role Change</h3>
            <p className="text-sm text-gray-600 mb-5">
              Change <strong>{confirm.user.email}</strong> from{' '}
              <RoleBadge role={confirm.user.role} size="sm" /> to{' '}
              <RoleBadge role={confirm.newRole} size="sm" />?
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setConfirm(null)} className="btn-secondary text-sm" disabled={assigning}>
                Cancel
              </button>
              <button onClick={confirmAssign} className="btn-primary text-sm flex items-center gap-2" disabled={assigning}>
                {assigning && <Loader2 size={14} className="animate-spin" />}
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
