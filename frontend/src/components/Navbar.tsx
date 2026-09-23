'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { History, Calendar, MessageSquare, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    api.checkHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  const navLinks = [
    { name: 'AI Mechanic', href: '/chat', icon: MessageSquare },
    { name: 'History', href: '/history', icon: History },
    { name: 'My Bookings', href: '/booking', icon: Calendar },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-stone-200 bg-white/90 backdrop-blur-md transition-all shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo & Tagline */}
        <Link href="/" className="flex items-center gap-3 transition-opacity hover:opacity-90">
          <div className="relative h-10 w-36 sm:w-44">
            <Image
              src="/brand-logo.png"
              alt="Instant Mechanic"
              fill
              className="object-contain"
              priority
            />
          </div>
          <span className="hidden md:inline-block rounded-full bg-orange-50 px-2.5 py-0.5 text-[11px] font-bold text-orange-600 border border-orange-200">
            गाड़ी खराब, मैकेनिक तैयार
          </span>
        </Link>

        {/* Center Nav Links */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-stone-900 text-white shadow-sm'
                    : 'text-stone-600 hover:bg-stone-100 hover:text-stone-950'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right: Emergency Helpline & Status */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Live Backend Badge */}
          <div className="hidden lg:flex items-center gap-2 text-[11px] font-medium text-stone-500 border border-stone-200 rounded-full px-3 py-1 bg-stone-50">
            <span
              className={`h-2 w-2 rounded-full ${
                backendOnline === true
                  ? 'bg-emerald-500 animate-pulse'
                  : backendOnline === false
                  ? 'bg-rose-500'
                  : 'bg-amber-500'
              }`}
            />
            <span>{backendOnline ? 'AI Diagnostic Online' : 'Connecting...'}</span>
          </div>

          {/* Helpline Phone */}
          <div className="hidden sm:flex flex-col text-right">
            <span className="text-[10px] uppercase font-bold tracking-wider text-stone-400">
              24/7 Helpline
            </span>
            <span className="text-xs font-bold text-stone-900 font-mono">
              +91 98765 43210
            </span>
          </div>

          {/* Quick CTA */}
          <Link
            href="/chat"
            className="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-2 text-xs font-bold text-white shadow-md transition-all hover:opacity-95 hover:shadow-orange-500/20 active:scale-95"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Diagnose Now</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
