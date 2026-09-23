'use client';

import React, { useEffect } from 'react';
import './TruckLoader.css';

export default function TruckLoader({ className = '' }: { className?: string }) {
  return (
    <div className={`loader ${className}`}>
      <div className="truckWrapper">
        {/* Lamp Post SVG moving across the background */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 30 90"
          className="lampPost"
          fill="none"
        >
          {/* Base */}
          <rect x="11" y="86" width="8" height="4" rx="1" fill="#282828" />
          {/* Post */}
          <line x1="15" y1="86" x2="15" y2="12" stroke="#282828" strokeWidth="2.5" strokeLinecap="round" />
          {/* Curved Arm */}
          <path d="M15 16 C15 4, 25 4, 25 14" stroke="#282828" strokeWidth="2" strokeLinecap="round" fill="none" />
          {/* Lantern Shade */}
          <polygon points="21,14 29,14 27,20 23,20" fill="#282828" />
          {/* Bulb */}
          <circle cx="25" cy="21" r="2" fill="#facc15" />
          {/* Street light beam cone */}
          <polygon points="23,22 14,90 32,90 27,22" fill="rgba(250, 204, 21, 0.12)" />
        </svg>

        {/* Truck Upper Body SVG with Instant Mechanic livery */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 130 50"
          className="truckBody"
          fill="none"
        >
          {/* Cargo Container Body */}
          <rect x="0" y="6" width="84" height="36" rx="2" fill="#dc2626" />
          <rect x="0" y="24" width="84" height="3" fill="#ffffff" />
          
          {/* White roof cap */}
          <rect x="0" y="6" width="84" height="3" rx="1" fill="#b91c1c" />
          
          {/* Decals on truck side */}
          <text x="6" y="19" fill="#ffffff" fontSize="6.5" fontWeight="900" fontFamily="monospace">
            INSTANT MECHANIC
          </text>
          <text x="6" y="34" fill="#ffffff" fontSize="4.8" fontWeight="bold" fontFamily="monospace">
            24×7 RAPID DISPATCH
          </text>

          {/* Van Cabin */}
          <path
            d="M84 13 L106 13 C110 13, 114 17, 116 22 L124 25 C127 27, 129 30, 129 33 L129 42 L84 42 Z"
            fill="#ffffff"
            stroke="#282828"
            strokeWidth="1.2"
          />

          {/* Windshield & Side Window */}
          <path d="M106 16 L115 24 L90 24 L90 16 Z" fill="#1e293b" opacity="0.85" />
          <rect x="91" y="26" width="12" height="1" fill="#cbd5e1" />

          {/* Headlight with forward beam */}
          <circle cx="127" cy="34" r="2.5" fill="#facc15" />
          <polygon points="129,34 142,30 142,40 129,36" fill="rgba(250, 204, 21, 0.25)" />

          {/* Front Grille and Bumper */}
          <rect x="127" y="38" width="3" height="4" rx="0.5" fill="#282828" />
          <rect x="0" y="38" width="3" height="4" fill="#282828" />

          {/* Wheel Cutouts in Chassis */}
          <circle cx="26" cy="42" r="13" fill="#faf9f5" />
          <circle cx="106" cy="42" r="13" fill="#faf9f5" />
        </svg>

        {/* Truck's Tires */}
        <div className="truckTires">
          {/* Front Tire */}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
            {/* Outer Tire Tread */}
            <circle cx="12" cy="12" r="11" fill="#1c1917" stroke="#44403c" strokeWidth="1.5" />
            {/* Rim */}
            <circle cx="12" cy="12" r="6" fill="#e7e5e4" />
            {/* Red Hub */}
            <circle cx="12" cy="12" r="2.5" fill="#dc2626" />
            {/* Spokes */}
            <line x1="12" y1="6" x2="12" y2="18" stroke="#78716c" strokeWidth="1" />
            <line x1="6" y1="12" x2="18" y2="12" stroke="#78716c" strokeWidth="1" />
          </svg>

          {/* Rear Tire */}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
            {/* Outer Tire Tread */}
            <circle cx="12" cy="12" r="11" fill="#1c1917" stroke="#44403c" strokeWidth="1.5" />
            {/* Rim */}
            <circle cx="12" cy="12" r="6" fill="#e7e5e4" />
            {/* Red Hub */}
            <circle cx="12" cy="12" r="2.5" fill="#dc2626" />
            {/* Spokes */}
            <line x1="12" y1="6" x2="12" y2="18" stroke="#78716c" strokeWidth="1" />
            <line x1="6" y1="12" x2="18" y2="12" stroke="#78716c" strokeWidth="1" />
          </svg>
        </div>

        {/* Road with passing dash animation */}
        <div className="road" />
      </div>
    </div>
  );
}

/**
 * Fullscreen / Overlay smooth loading transition for opening the chat bot
 */
export function TruckLoaderOverlay({
  message = 'CONNECTING TO DIAGNOSTICS...',
  subMessage = 'Initializing diagnostic workspace...',
  fadeOut = false
}: {
  message?: string;
  subMessage?: string;
  fadeOut?: boolean;
}) {
  useEffect(() => {
    if (!fadeOut) {
      const prevBodyOverflow = document.body.style.overflow;
      const prevHtmlOverflow = document.documentElement.style.overflow;
      document.body.style.overflow = 'hidden';
      document.documentElement.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = prevBodyOverflow;
        document.documentElement.style.overflow = prevHtmlOverflow;
      };
    }
  }, [fadeOut]);

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#faf9f5] overflow-hidden select-none transition-opacity duration-500 ease-out ${
        fadeOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      {/* Background subtle grid */}
      <div
        className="absolute inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 50%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 50%, #000 70%, transparent 100%)'
        }}
      />

      {/* Centered Truck Loader Card */}
      <div className="relative z-10 flex flex-col items-center text-center p-8 max-w-sm rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md shadow-xs">
        {/* Animated Truck Component */}
        <TruckLoader />

        {/* Loading status text */}
        <div className="mt-6 space-y-1.5">
          <span className="text-xs font-mono font-bold tracking-wider text-black block iosevka-charon-bold uppercase">
            {message}
          </span>
          <span className="text-[11px] font-mono text-stone-500 block">
            {subMessage}
          </span>
        </div>

        {/* Smooth loading progress indicator */}
        <div className="mt-4 w-40 h-1 bg-stone-200 rounded-full overflow-hidden relative">
          <div className="h-full bg-red-600 rounded-full truck-progress-bar" style={{ width: '45%' }} />
        </div>
      </div>
    </div>
  );
}

