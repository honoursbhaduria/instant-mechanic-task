'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import {
  AutomotiveBattery01Icon,
  Car01Icon,
  Rocket01Icon,
  Settings02Icon,
  Location01Icon,
  ShieldCheckIcon,
  Call02Icon,
  Layers01Icon,
} from '@hugeicons/core-free-icons';
import BranchedMenu, { BranchedMenuItem } from './BranchedMenu';
import { Phone, ChevronDown, X, Sparkles, MessageSquare } from 'lucide-react';

export default function Navbar() {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuContainerRef = useRef<HTMLDivElement>(null);

  // Menu items with black text labels matching user request
  const branchedMenuItems: BranchedMenuItem[] = [
    {
      label: 'Car Services',
      children: [
        { value: '#services', label: '20-Min Roadside Help', icon: AutomotiveBattery01Icon },
        { value: '#services', label: 'Battery Jumpstart', icon: AutomotiveBattery01Icon },
        { value: '#services', label: 'Flat Tyre & Towing', icon: Car01Icon },
        { value: '#promises', label: 'Trusted Garage Repairs', icon: Settings02Icon },
      ]
    },
    {
      label: 'AI Diagnosis',
      children: [
        { value: '/chat', label: 'IM Buddy (Free Tool)', icon: Rocket01Icon },
        { value: '#ai-section', label: '10,000+ Symptom Map', icon: ShieldCheckIcon },
      ]
    },
    {
      label: 'Membership',
      children: [
        { value: '#membership', label: 'Car Care Plan (₹1,599/yr)', icon: Layers01Icon },
        { value: '#membership', label: 'Unlimited Call-Outs', icon: ShieldCheckIcon },
      ]
    },
    {
      label: 'Coverage & Areas',
      children: [
        { value: '#coverage', label: 'Delhi NCR (500+ Techs)', icon: Location01Icon },
        { value: '#coverage', label: 'Sector 75 Gurugram HQ', icon: Location01Icon },
      ]
    },
    {
      label: 'Emergency Contact',
      children: [
        { value: 'tel:+919266961110', label: '+91 9266961110 (24x7)', icon: Call02Icon },
        { value: 'https://wa.me/919266961110', label: 'WhatsApp Dispatch', icon: <MessageSquare className="h-4 w-4 text-stone-700" /> },
      ]
    }
  ];

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setMenuOpen(true);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setMenuOpen(false);
    }, 220);
  };

  // Handle outside click to close dropdown menu
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuContainerRef.current && !menuContainerRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleSelect = (value: string) => {
    setMenuOpen(false);
    if (value.startsWith('tel:') || value.startsWith('https:')) {
      window.open(value, '_blank');
      return;
    }
    if (value.startsWith('/')) {
      router.push(value);
      return;
    }
    if (value.startsWith('#')) {
      const el = document.querySelector(value);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <header className="fixed top-3 sm:top-5 inset-x-0 z-50 flex justify-center px-2 sm:px-3 pointer-events-none">
      <div ref={menuContainerRef} className="relative w-full max-w-5xl pointer-events-auto">
        {/* Floating Bar - clean, minimalist, flat with subtle border and no shadow */}
        <div className="relative rounded-full bg-white/95 backdrop-blur-md border border-stone-200 px-2.5 sm:px-4 py-2 sm:py-2.5 flex items-center justify-between transition-all">
          
          {/* Left: Brand Logo in Crisp Clean Container */}
          <Link href="/" className="flex items-center transition-opacity hover:opacity-90 shrink-0">
            <div className="relative h-6 w-24 sm:w-28">
              <Image
                src="/brand-logo.png"
                alt="Instant Mechanic Logo"
                fill
                className="object-contain"
                priority
              />
            </div>
          </Link>

          {/* Center: Interactive BranchedMenu Trigger & Direct Links */}
          <div className="flex items-center gap-1 sm:gap-3">
            {/* The BranchedMenu Toggle Button with auto hover-to-open */}
            <div
              className="relative inline-flex"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className={`inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 rounded-full text-xs font-bold tracking-wide transition-colors ${
                  menuOpen
                    ? 'bg-stone-900 text-white'
                    : 'bg-stone-100 hover:bg-stone-200 text-stone-900 border border-stone-200'
                }`}
              >
                <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-600" />
                <span>Menu & Services</span>
                <ChevronDown className={`h-3.5 w-3.5 transition-transform duration-200 ${menuOpen ? 'rotate-180' : ''}`} />
              </button>
            </div>

            {/* Quick Desktop Links in crisp black text */}
            <nav className="hidden lg:flex items-center gap-5 text-xs font-bold text-black ml-1">
              <a href="#services" className="hover:text-red-600 transition-colors">
                Roadside
              </a>
              <Link href="/chat" className="hover:text-red-600 transition-colors">
                AI Diagnosis
              </Link>
              <a href="#membership" className="hover:text-red-600 transition-colors">
                Membership
              </a>
              <a href="#coverage" className="hover:text-red-600 transition-colors">
                Coverage
              </a>
            </nav>
          </div>

          {/* Right: Phone CTA & Book Action */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Direct 24/7 Phone Call */}
            <a
              href="tel:+919266961110"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono font-bold text-stone-900 hover:text-red-600 transition-colors bg-stone-100 border border-stone-200 rounded-full px-3 py-1.5"
            >
              <Phone className="h-3 w-3 text-red-600" />
              <span>+91 9266961110</span>
            </a>

            {/* Primary Action Button - Shining Metal Effect */}
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-3.5 sm:px-4 py-1.5 text-xs font-semibold active:scale-95 whitespace-nowrap"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10 animate-pulse" />
              <span className="relative z-10">Free AI Check</span>
            </Link>
          </div>
        </div>

        {/* BranchedMenu Dropdown Drawer - Glassmorphism, light card, black text */}
        {menuOpen && (
          <div
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-full max-w-md rounded-2xl bg-white/95 backdrop-blur-md border border-stone-200 p-5 text-left z-50 shadow-lg animate-in fade-in slide-in-from-top-2 duration-150"
          >
            <div className="flex items-center justify-between pb-3 mb-2 border-b border-stone-100">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-600" />
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-stone-900">
                  Instant Mechanic OS • Delhi NCR 24×7
                </span>
              </div>
              <button
                onClick={() => setMenuOpen(false)}
                className="text-stone-400 hover:text-stone-900 p-1 rounded-full transition-colors"
                aria-label="Close Menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* The BranchedMenu Component with black text and subtle lines */}
            <div className="py-2 flex justify-start">
              <BranchedMenu
                items={branchedMenuItems}
                defaultOpen={[0, 1]}
                defaultActive="20-Min Roadside Help"
                onSelect={handleSelect}
                color="#09090b"
                accentColor="#dc2626"
                lineColor="#e4e4e7"
                width={380}
                rowHeight={36}
                indent={44}
                trunk={14}
                radius={10}
                lineWidth={1.5}
                fontSize={13}
                drawDuration={300}
                foldDuration={200}
              />
            </div>

            {/* Quick Contact Footer inside BranchedMenu Drawer */}
            <div className="mt-4 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
              <span className="text-stone-900 font-bold text-[11px]">Direct Roadside Dispatch:</span>
              <a
                href="tel:+919266961110"
                className="font-mono font-bold text-red-600 hover:underline flex items-center gap-1"
              >
                <Phone className="h-3 w-3" />
                <span>+91 9266961110</span>
              </a>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
