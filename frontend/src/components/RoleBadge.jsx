import { Shield, Pencil, Eye } from 'lucide-react';

const config = {
  ADMIN: { color: 'bg-red-100 text-red-700', icon: Shield, label: 'Admin' },
  EDITOR: { color: 'bg-blue-100 text-blue-700', icon: Pencil, label: 'Editor' },
  VIEWER: { color: 'bg-gray-100 text-gray-600', icon: Eye, label: 'Viewer' },
};

export default function RoleBadge({ role, size = 'md' }) {
  const c = config[role] || config.VIEWER;
  const Icon = c.icon;
  const sizes = size === 'sm'
    ? 'text-[10px] px-1.5 py-0.5 gap-1'
    : 'text-xs px-2 py-1 gap-1.5';

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${c.color} ${sizes}`}>
      <Icon size={size === 'sm' ? 10 : 12} />
      {c.label}
    </span>
  );
}
