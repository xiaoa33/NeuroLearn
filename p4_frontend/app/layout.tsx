'use client';

import './globals.css';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { useSession } from '@/hooks/useSession';
import { BehaviorTracker } from '@/components/state/BehaviorTracker';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useSession();

  return (
    <html lang="zh-CN">
      <body className="bg-gray-50">
        <Sidebar />
        <TopBar />
        <main className="ml-16 pt-16 min-h-screen">
          <div className="p-6">
            {children}
          </div>
        </main>
        <BehaviorTracker />
      </body>
    </html>
  );
}