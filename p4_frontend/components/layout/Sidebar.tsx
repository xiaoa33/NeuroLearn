import { LayoutDashboard, BookOpen, HelpCircle, RefreshCw, BarChart3 } from 'lucide-react';
import { usePathname } from 'next/navigation';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: '仪表盘' },
  { path: '/learn', icon: BookOpen, label: '学习' },
  { path: '/quiz', icon: HelpCircle, label: '测验' },
  { path: '/review', icon: RefreshCw, label: '复习' },
  { path: '/insights', icon: BarChart3, label: '洞察' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6 z-50">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-8">
        <span className="text-white font-bold text-lg">N</span>
      </div>
      
      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          
          return (
            <a
              key={item.path}
              href={item.path}
              className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 group relative ${
                isActive
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                {item.label}
              </span>
            </a>
          );
        })}
      </nav>
    </aside>
  );
}