'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import ParticleText from '@/components/ParticleText';
import FoldText from '@/components/FoldText';
import CRTWarp from '@/components/CRTWarp';
import {
  Sparkles,
  ArrowRight,
  Phone,
  MessageSquare,
  ShieldCheck,
  Check,
  Star,
  Zap,
  MoreHorizontal,
  FileText,
  FileCode,
  Wrench,
  Car,
  Fuel,
  Key,
  Clock,
  Tag,
  MapPin,
  Globe
} from 'lucide-react';

export default function HomePage() {
  const [activeFoundationIndex, setActiveFoundationIndex] = useState(0);

  const realReviews = [
    {
      name: 'Shashank Singh',
      role: 'Gurugram · Google Review',
      initials: 'SS',
      text: 'My car broke down at 11pm on NH48. Called Instant Mechanic, within 12 minutes a mechanic was there. Towed from DLF Gurugram to Rohini without any hassle. Outstanding service.'
    },
    {
      name: 'Udit Kumar',
      role: 'Noida · Google Review',
      initials: 'UK',
      text: 'While going to office my car suddenly stopped at Vatika Business Park. Found Instant Mechanic, they came fast and fixed it. Very professional and efficient team.'
    },
    {
      name: 'Amit Kumar',
      role: 'Faridabad · Google Review',
      initials: 'AK',
      text: 'On my way home I had a flat tyre. Found them online, sent a mechanic within 20 minutes and solved the problem on the spot. Awesome service within the time!'
    },
    {
      name: 'Priya Kapoor',
      role: 'Delhi · Google Review',
      initials: 'PK',
      text: 'As a woman driving alone, I was scared when my battery died. Instant Mechanic sent a KYC-verified mechanic and I felt completely safe. Will always keep this number saved.'
    },
    {
      name: 'Amit Malhotra',
      role: 'Ghaziabad · Google Review',
      initials: 'AM',
      text: 'Needed towing after an accident. Under 15 minutes arrival, completely professional, charged exactly what they quoted. No hidden bills. Amazing team.'
    },
    {
      name: 'Vikram Tandon',
      role: 'DLF Phase 2 · Member',
      initials: 'VT',
      text: "Got the membership and it's worth every rupee. Three call-outs this year, each time under 20 minutes. The bill transparency alone makes it worthwhile."
    }
  ];

  const coverageAreas = [
    'Gurugram',
    'Delhi',
    'Noida',
    'Faridabad',
    'Ghaziabad',
    'Greater Noida',
    'Manesar',
    'Dwarka',
    'Rohini',
    'NH48 / NH8',
    'DND Corridor',
    'Indirapuram'
  ];

  return (
    <div className="min-h-screen bg-[#faf9f5] text-stone-900 font-sans relative overflow-x-clip selection:bg-red-600 selection:text-white">
      {/* Background Subtle Tech Grid Layer matching reference */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)'
        }}
      />

      {/* Floating Capsule Bar with BranchedMenu */}
      <Navbar />

      {/* ============================================================== */}
      {/* 1. HERO SECTION (CLEAN FLAT MINIMALIST AESTHETIC - NO SHADOWS) */}
      {/* ============================================================== */}
      <section className="relative z-10 pt-28 sm:pt-36 pb-16 sm:pb-20 px-2 sm:px-4 lg:px-6 max-w-7xl mx-auto flex flex-col items-center text-center">

        {/* Big Bold Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-black leading-[1.08] max-w-4xl mx-auto iosevka-charon-bold">
          Your Car Deserves <br />
          <span className="font-extrabold text-black">Expert Care, Not a Gamble.</span>
        </h1>

        {/* Hindi Tagline */}
        <div className="mt-3 text-sm sm:text-base font-bold text-red-600 tracking-wide font-mono">
          गाड़ी खराब, मेकैनिक तैयार — Car broken, Mechanic ready.
        </div>

        {/* Description from Real Website */}
        <p className="mt-4 text-sm sm:text-base text-stone-900 max-w-2xl mx-auto font-medium leading-relaxed">
          One platform for every car need — instant roadside help in 20 minutes, AI-powered diagnosis, transparent repair bills, and complete car care membership. Delhi NCR&apos;s most trusted car care company.
        </p>

        {/* Action Cards / Buttons with shining metal effect on Free AI Check */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
          {/* Card 1: Try AI Diagnosis — Free (Shining Metal Effect - No Bottom Shadow) */}
          <Link
            href="/chat"
            className="btn-metal-shine inline-flex items-center gap-2 rounded-full px-6 sm:px-7 py-3 text-xs sm:text-sm font-bold active:scale-95"
          >
            <Sparkles className="h-4 w-4 text-amber-400 relative z-10 animate-pulse" />
            <span className="relative z-10">Try AI Diagnosis — Free</span>
            <ArrowRight className="h-4 w-4 text-stone-300 relative z-10" />
          </Link>

          {/* Card 2: Call Now */}
          <a
            href="tel:+919266961110"
            className="inline-flex items-center gap-2 rounded-full bg-white hover:bg-stone-100 text-stone-950 border border-stone-300 px-6 sm:px-7 py-3 text-xs sm:text-sm font-bold transition-colors active:scale-95"
          >
            <Phone className="h-4 w-4 text-red-600" />
            <span>Call Now: +91 9266961110</span>
          </a>

          {/* Card 3: WhatsApp Us */}
          <a
            href="https://wa.me/919266961110"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-full bg-white hover:bg-stone-100 text-stone-950 border border-stone-300 px-5 sm:px-6 py-3 text-xs sm:text-sm font-bold transition-colors active:scale-95"
          >
            <MessageSquare className="h-4 w-4 text-stone-800" />
            <span>WhatsApp Us</span>
          </a>
        </div>

        {/* ============================================================== */}
        {/* HERO SHOWCASE CARD (GLASSMORPHISM)                            */}
        {/* ============================================================== */}
        <div className="mt-12 sm:mt-16 w-full max-w-5xl">
          <div className="relative rounded-2xl sm:rounded-3xl border border-white/80 bg-white/70 backdrop-blur-md p-6 sm:p-12 lg:p-14 overflow-hidden shadow-xs">
            {/* Inner subtle grid inside hero card */}
            <div className="absolute inset-0 bg-grid-fine opacity-25 pointer-events-none" />

            {/* Center: Hero Graphic matching background */}
            <div className="relative z-10 flex items-center justify-center py-2 sm:py-6">
              <div className="relative w-full max-w-3xl h-64 sm:h-96 md:h-[420px] flex items-center justify-center">
                <Image
                  src="/hero-image.png"
                  alt="गाड़ी खराब, मेकैनिक तैयार — Instant Mechanic"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
            </div>
          </div>
        </div>

        {/* 4 Live Stats Strip from Real Website - Glassmorphism */}
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 w-full max-w-4xl">
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-4 text-center shadow-xs">
            <span className="text-2xl sm:text-3xl font-black text-black block font-mono">30,000+</span>
            <span className="text-xs text-stone-800 font-semibold">Cars Served Across NCR</span>
          </div>
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-4 text-center shadow-xs">
            <div className="flex items-center justify-center gap-1">
              <span className="text-2xl sm:text-3xl font-black text-black font-mono">4.9</span>
              <Star className="h-5 w-5 fill-amber-400 text-amber-400" />
            </div>
            <span className="text-xs text-stone-800 font-semibold">Google Rating (1,500+ Reviews)</span>
          </div>
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-4 text-center shadow-xs">
            <span className="text-2xl sm:text-3xl font-black text-black block font-mono">20 min</span>
            <span className="text-xs text-stone-800 font-semibold">Fastest Response in NCR</span>
          </div>
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-4 text-center shadow-xs">
            <span className="text-2xl sm:text-3xl font-black text-black block font-mono">24×7</span>
            <span className="text-xs text-stone-800 font-semibold">Always Available, 365 Days</span>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 2. PARTICLETEXT INTERACTIVE SECTION (REACT BITS INTEGRATION)   */}
      {/* ============================================================== */}
      <section className="relative z-10 py-6 sm:py-8 bg-transparent">
        <div className="max-w-6xl mx-auto px-2 sm:px-4 lg:px-6 text-center">
          {/* Interactive ParticleText Canvas in pure solid black, flat, no glow */}
          <div className="w-full h-64 sm:h-72 relative flex items-center justify-center cursor-pointer">
            <ParticleText
              text="INSTANT MECHANIC"
              particleSize={2}
              density={4}
              color="#09090b"
              highlightColor="#27272a"
              scatter={160}
              gatherDuration={1500}
              stagger={380}
              pointerRepel={40}
              repelRadius={120}
              idleDrift={0.6}
              trigger="hover"
              fontSize="clamp(2.5rem, 8vw, 5.5rem)"
              fontWeight={900}
              glow={false}
            />
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 3. OUR THREE PROMISES (THREE PILLARS. ONE PROMISE)             */}
      {/* ============================================================== */}
      <section id="promises" className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto text-left">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
            OUR THREE PROMISES
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-black">
            Three Pillars. One Promise.
          </h2>
          <p className="mt-3 text-sm text-stone-900 font-medium">
            We&apos;re not a mechanic booking app. We&apos;re building the operating system for car ownership in India.
          </p>
        </div>

        {/* Desktop: 3-column Grid | Mobile: Stacking Cards Effect (No Glow) */}
        <div className="relative flex flex-col space-y-6 md:grid md:grid-cols-3 md:gap-6 md:space-y-0 pb-16 md:pb-0">
          {/* Pillar 1 */}
          <div className="sticky top-20 sm:top-24 z-10 md:static md:top-auto md:z-auto rounded-3xl border border-stone-300 bg-white p-6 sm:p-7 flex flex-col justify-between space-y-4 hover:border-stone-400 transition-all">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-stone-500 mb-3">
                <span className="font-bold text-black px-2 py-0.5 rounded-md bg-stone-100 border border-stone-200">01 — The Core</span>
                <span className="flex items-center gap-1 font-semibold text-black">
                  <Zap className="h-3.5 w-3.5 text-red-600" />
                  Fast Response
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-black iosevka-charon-bold">
                20-Min Mechanic, Anywhere
              </h3>
              <p className="text-xs sm:text-sm text-stone-900 mt-2 leading-relaxed font-normal">
                Battery jumpstart, tyre change, towing, fuel delivery — a verified mechanic reaches you within 20 minutes anywhere in Delhi NCR. Parts carried on-board for instant fix.
              </p>
            </div>
            <div className="pt-3 border-t border-stone-200 flex items-center gap-1.5 text-xs font-bold text-black">
              <Check className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>Live Now Across NCR</span>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="sticky top-28 sm:top-32 z-20 md:static md:top-auto md:z-auto rounded-3xl border border-stone-300 bg-white p-6 sm:p-7 flex flex-col justify-between space-y-4 hover:border-stone-400 transition-all">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-stone-500 mb-3">
                <span className="font-bold text-black px-2 py-0.5 rounded-md bg-stone-100 border border-stone-200">02 — The Guarantee</span>
                <span className="flex items-center gap-1 font-semibold text-black">
                  <Clock className="h-3.5 w-3.5 text-red-600" />
                  365 Days
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-black iosevka-charon-bold">
                24×7 Availability
              </h3>
              <p className="text-xs sm:text-sm text-stone-900 mt-2 leading-relaxed font-normal">
                Breakdowns don&apos;t wait for business hours. Neither do we. One call connects you to help at 2am, on a highway, on a Sunday — every single day of the year, 365 days.
              </p>
            </div>
            <div className="pt-3 border-t border-stone-200 flex items-center gap-1.5 text-xs font-bold text-black">
              <Check className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>Always On</span>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="sticky top-36 sm:top-40 z-30 md:static md:top-auto md:z-auto rounded-3xl border border-stone-300 bg-white p-6 sm:p-7 flex flex-col justify-between space-y-4 hover:border-stone-400 transition-all">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-stone-500 mb-3">
                <span className="font-bold text-black px-2 py-0.5 rounded-md bg-stone-100 border border-stone-200">03 — The Standard</span>
                <span className="flex items-center gap-1 font-semibold text-black">
                  <Wrench className="h-3.5 w-3.5 text-red-600" />
                  Gurugram HQ
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-black iosevka-charon-bold">
                Trusted Garage, Transparent Bills
              </h3>
              <p className="text-xs sm:text-sm text-stone-900 mt-2 leading-relaxed font-normal">
                Modern garage in Sector 75, Gurugram. Diagnosis-led repairs — AI recommends, mechanic executes, you approve. No hidden charges, no blind trust. Ever.
              </p>
            </div>
            <div className="pt-3 border-t border-stone-200 flex items-center gap-1.5 text-xs font-bold text-black">
              <Check className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>Book Today</span>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 4. WHAT WE DO (ROADSIDE ASSISTANCE IN 20 MINUTES)              */}
      {/* ============================================================== */}
      <section id="services" className="relative z-10 py-16 sm:py-20 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto">
        <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md p-8 sm:p-12 shadow-xs">
          <div className="max-w-3xl text-left">
            <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
              WHAT WE DO • ONE NUMBER
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-black">
              Every Car Need. One Number.
            </h2>
            <p className="text-xs sm:text-sm text-stone-900 mt-2 leading-relaxed font-medium">
              From emergency roadside rescue to complete car care — everything handled fast, 24 hours a day across Delhi NCR.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 text-left">
            <div className="p-4 rounded-2xl border border-stone-200/80 bg-white/80 hover:bg-white backdrop-blur-sm transition-all shadow-xs">
              <Zap className="h-5 w-5 text-black mb-2" />
              <h4 className="text-xs font-bold text-black">Battery Jumpstart</h4>
              <p className="text-[11px] text-stone-800 mt-1">Under 20 min arrival</p>
            </div>

            <div className="p-4 rounded-2xl border border-stone-200/80 bg-white/80 hover:bg-white backdrop-blur-sm transition-all shadow-xs">
              <Wrench className="h-5 w-5 text-black mb-2" />
              <h4 className="text-xs font-bold text-black">Flat Tyre Fix</h4>
              <p className="text-[11px] text-stone-800 mt-1">Puncture or spare swap</p>
            </div>

            <div className="p-4 rounded-2xl border border-stone-200/80 bg-white/80 hover:bg-white backdrop-blur-sm transition-all shadow-xs">
              <Car className="h-5 w-5 text-black mb-2" />
              <h4 className="text-xs font-bold text-black">Safe Towing</h4>
              <p className="text-[11px] text-stone-800 mt-1">Flatbed & wheel-lift</p>
            </div>

            <div className="p-4 rounded-2xl border border-stone-200/80 bg-white/80 hover:bg-white backdrop-blur-sm transition-all shadow-xs">
              <Fuel className="h-5 w-5 text-black mb-2" />
              <h4 className="text-xs font-bold text-black">Fuel Delivery</h4>
              <p className="text-[11px] text-stone-800 mt-1">Petrol or diesel on-spot</p>
            </div>

            <div className="p-4 rounded-2xl border border-stone-200/80 bg-white/80 hover:bg-white backdrop-blur-sm transition-all shadow-xs col-span-2 sm:col-span-1">
              <Key className="h-5 w-5 text-black mb-2" />
              <h4 className="text-xs font-bold text-black">Key Lockout</h4>
              <p className="text-[11px] text-stone-800 mt-1">Non-destructive entry</p>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-stone-200 flex flex-wrap items-center justify-between gap-4">
            <span className="text-xs font-bold text-stone-900 flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>500+ verified mechanics active on Delhi NCR roads right now.</span>
            </span>
            <a
              href="tel:+919266961110"
              className="inline-flex items-center gap-2 rounded-full bg-stone-900 hover:bg-black text-white px-5 py-2.5 text-xs font-bold transition-colors active:scale-95"
            >
              <Phone className="h-3.5 w-3.5 text-white" />
              <span>Call for Help Now (+91 9266961110)</span>
            </a>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 5. PREDICTIVE INTELLIGENCE (REACT BITS FOLDTEXT)               */}
      {/* ============================================================== */}
      <section className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto">
        <div className="relative flex items-center justify-center">
          {/* Centered Large Bold Title with FoldText */}
          <div className="text-center z-10 space-y-2 flex flex-col items-center">
            <h2 className="sr-only">Predictive Intelligence</h2>
            <div className="flex flex-col items-center justify-center leading-none">
              <FoldText
                text="Predictive"
                splitBy="char"
                hinge="top"
                trigger="scroll"
                duration={0.65}
                stagger={0.045}
                ease="power3.out"
                perspective={700}
                creaseShading={0.55}
                fontSize="clamp(3.2rem, 8vw, 6.2rem)"
                fontWeight={900}
                color="#0a0a0a"
                className="tracking-tight"
              />
              <FoldText
                text="Intelligence"
                splitBy="char"
                hinge="top"
                trigger="scroll"
                duration={0.65}
                stagger={0.045}
                ease="power3.out"
                perspective={700}
                creaseShading={0.55}
                fontSize="clamp(3.2rem, 8vw, 6.2rem)"
                fontWeight={900}
                color="#0a0a0a"
                className="tracking-tight mt-1"
              />
            </div>
            <p className="text-xs sm:text-sm text-stone-600 font-mono tracking-wider pt-3">
              REAL-TIME MECHANICAL TELEMETRY & 10,000+ REPAIR PATTERNS
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 6. AI DIAGNOSIS · FREE TO USE (KNOW WHAT'S WRONG BEFORE CALL) */}
      {/* ============================================================== */}
      <section id="ai-section" className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          
          {/* Left Column: Glassmorphism Container with File Hierarchy Card */}
          <div className="lg:col-span-6 bg-white/70 backdrop-blur-md rounded-3xl p-6 sm:p-10 border border-white/80 shadow-xs flex items-center justify-center">
            <div className="w-full max-w-md rounded-2xl bg-white/85 backdrop-blur-sm border border-stone-200/80 p-5 text-left shadow-xs">
              {/* Card Header */}
              <div className="flex items-center justify-between pb-4 border-b border-stone-200">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-stone-900">IM Buddy Diagnostic Report</span>
                  <span className="text-[10px] bg-stone-100 text-stone-800 px-1.5 py-0.5 rounded font-mono font-bold">Live</span>
                </div>
                <MoreHorizontal className="h-4 w-4 text-stone-500 cursor-pointer" />
              </div>

              {/* File List Items */}
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-stone-50 transition-colors cursor-pointer group">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-stone-100 text-stone-800 rounded-md">
                      <FileText className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-stone-900">
                        Symptom_Pattern_Analysis.log
                      </p>
                      <p className="text-[10px] text-stone-500 font-mono">10,000+ Repair Patterns</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-stone-900 font-bold bg-stone-100 px-2 py-0.5 rounded">
                    MATCHED
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-stone-50 transition-colors cursor-pointer group">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-stone-100 text-stone-800 rounded-md">
                      <FileCode className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-stone-900">
                        Fair_Price_Estimate.json
                      </p>
                      <p className="text-[10px] text-stone-500 font-mono">Upfront Market Rate Verified</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-stone-900 font-bold bg-stone-100 px-2 py-0.5 rounded">
                    SYNCED
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-stone-50 transition-colors cursor-pointer group">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-stone-100 text-stone-800 rounded-md">
                      <ShieldCheck className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-stone-900">
                        Drive_Safety_Rating.pdf
                      </p>
                      <p className="text-[10px] text-stone-500 font-mono">Green/Yellow/Red Urgency</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-stone-900 font-bold bg-stone-100 px-2 py-0.5 rounded">
                    SAFE
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Structured Text with Red Accent Bar */}
          <div className="lg:col-span-6 space-y-6 text-left">
            <div className="space-y-1">
              <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block">
                AI-POWERED · FREE TO USE
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-stone-950">
                Know What&apos;s Wrong Before You Call Anyone.
              </h2>
            </div>

            <p className="text-xs sm:text-sm text-stone-700 leading-relaxed">
              India&apos;s first conversational car self-diagnosis tool. Describe your symptoms — our AI identifies likely causes, estimates repair cost, and tells you if it&apos;s safe to drive.
            </p>

            <div className="space-y-6">
              {/* Feature 1 */}
              <div 
                onClick={() => setActiveFoundationIndex(0)}
                className={`pl-4 border-l-2 cursor-pointer transition-all ${
                  activeFoundationIndex === 0 ? 'border-red-600' : 'border-stone-300 opacity-60'
                }`}
              >
                <h3 className="text-sm font-bold text-stone-900">
                  Symptom-based diagnosis
                </h3>
                <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                  Describe what you hear, see, or feel — AI maps it to probable causes using 10,000+ repair patterns.
                </p>
              </div>

              {/* Feature 2 */}
              <div 
                onClick={() => setActiveFoundationIndex(1)}
                className={`pl-4 border-l-2 cursor-pointer transition-all ${
                  activeFoundationIndex === 1 ? 'border-red-600' : 'border-stone-300 opacity-60'
                }`}
              >
                <h3 className="text-sm font-bold text-stone-900">
                  Fair price estimate, upfront
                </h3>
                <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                  Know market rate before a mechanic arrives. Never get overcharged again.
                </p>
              </div>

              {/* Feature 3 */}
              <div 
                onClick={() => setActiveFoundationIndex(2)}
                className={`pl-4 border-l-2 cursor-pointer transition-all ${
                  activeFoundationIndex === 2 ? 'border-red-600' : 'border-stone-300 opacity-60'
                }`}
              >
                <h3 className="text-sm font-bold text-stone-900">
                  Drive or don&apos;t drive?
                </h3>
                <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                  Clear green/yellow/red urgency rating. Act on facts, not fear.
                </p>
              </div>
            </div>

            <div className="pt-2">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-full bg-stone-900 hover:bg-black text-white px-6 py-3 text-xs font-bold transition-colors active:scale-95"
              >
                <Sparkles className="h-4 w-4 text-amber-400" />
                <span>Try IM Buddy — Free</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 7. CAR CARE MEMBERSHIP (ONE PLAN. COMPLETE PEACE OF MIND)     */}
      {/* ============================================================== */}
      <section id="membership" className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
            CAR CARE MEMBERSHIP
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-stone-950">
            One Plan. Complete Peace of Mind.
          </h2>
          <p className="mt-3 text-sm text-stone-700">
            Delhi NCR&apos;s most comprehensive annual car care plan. Everything your car needs under one simple subscription.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: 6 Feature Highlights - Glassmorphism */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <Phone className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">Unlimited Emergencies</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">Call us anytime, as many times as needed</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <Clock className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">Priority Dispatch</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">Members jump the queue — faster response</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <ShieldCheck className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">Annual Health Check</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">1 free 40-point inspection per year</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <Tag className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">20% Off All Repairs</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">Every garage visit, every service</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <Sparkles className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">AI Diagnosis Included</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">Unlimited IM Buddy access</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/75 backdrop-blur-md border border-white/80 shadow-xs">
              <FileText className="h-5 w-5 text-stone-800 mb-1" />
              <h4 className="text-xs font-bold text-stone-900">Digital Service History</h4>
              <p className="text-[11px] text-stone-600 mt-0.5">Every job recorded, accessible anytime</p>
            </div>
          </div>

          {/* Right Column: Pricing Subscription Box with CRTWarp at top fading at 1/4th */}
          <div className="lg:col-span-5 rounded-3xl bg-[#121214] text-white p-6 sm:p-8 border border-stone-800 text-left relative overflow-hidden">
            {/* Top 1/4 CRTWarp Ambient Animation */}
            <div
              className="absolute inset-x-0 top-0 h-40 sm:h-48 pointer-events-none z-0 overflow-hidden"
              style={{
                maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0.7) 40%, rgba(0,0,0,0) 100%)',
                WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0.7) 40%, rgba(0,0,0,0) 100%)'
              }}
            >
              <CRTWarp
                color="#ef4444"
                backgroundColor="#121214"
                speed={0.4}
                curvature={0.2}
                scanlineStrength={0.25}
                scanlineFrequency={160}
                waveAmplitude={0.25}
                waveFrequency={2.2}
                bloom={1.2}
                bloomRadius={0.8}
                noise={0.06}
                brightness={1.15}
                mouseReact
                mouseStrength={0.35}
                fps={30}
              />
            </div>

            <div className="relative z-10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono uppercase tracking-widest text-stone-400">
                  CAR CARE PLAN
                </span>
                <span className="rounded-full bg-red-600 px-3 py-1 text-[10px] font-mono font-bold tracking-wider uppercase text-white">
                  BEST VALUE
                </span>
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-4xl font-black font-mono">₹1,599</span>
                <span className="text-xs text-stone-400 font-mono">/ year</span>
              </div>
              <p className="text-xs text-stone-400 mt-1">That&apos;s just ₹125/month</p>

            <ul className="mt-6 space-y-2.5 text-xs text-stone-300">
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>Unlimited emergency call-outs</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>Priority dispatch — jump the queue</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>1 free annual car health check</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>20% off all garage repairs</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>AI diagnosis — unlimited access</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>Transparent bill guarantee</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-red-500 shrink-0" />
                <span>Digital service history</span>
              </li>
            </ul>

            <div className="mt-8 pt-6 border-t border-stone-800 space-y-2">
              <Link
                href="/booking"
                className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-white hover:bg-stone-200 text-stone-950 py-3 text-xs font-bold transition-colors active:scale-95"
              >
                <span>Get Membership →</span>
              </Link>
              <p className="text-center text-[10px] text-stone-400">
                Pay once · Valid 12 months
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

      {/* ============================================================== */}
      {/* 8. SIMPLE 4-STEP PROCESS (MECHANIC AT YOUR DOOR IN 4 STEPS)   */}
      {/* ============================================================== */}
      <section className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
            SIMPLE PROCESS
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-stone-950">
            Mechanic at Your Door in 4 Steps.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
          {/* Step 1 */}
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-5 flex flex-col justify-between space-y-3 shadow-xs">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-red-600">01</span>
                <Phone className="h-4 w-4 text-stone-700" />
              </div>
              <h3 className="text-sm font-bold text-stone-900 mt-2">
                Call or WhatsApp
              </h3>
              <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                Dial +91 9266961110 or WhatsApp us. Tell us your issue — takes under a minute.
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-5 flex flex-col justify-between space-y-3 shadow-xs">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-red-600">02</span>
                <MapPin className="h-4 w-4 text-stone-700" />
              </div>
              <h3 className="text-sm font-bold text-stone-900 mt-2">
                Share Location
              </h3>
              <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                Drop your live location pin. We cover all of Delhi NCR — highway, mall, home, office.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-5 flex flex-col justify-between space-y-3 shadow-xs">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-red-600">03</span>
                <Car className="h-4 w-4 text-stone-700" />
              </div>
              <h3 className="text-sm font-bold text-stone-900 mt-2">
                Mechanic Dispatched
              </h3>
              <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                A KYC-verified, uniformed mechanic is on the way — GPS tracked, ETA on WhatsApp.
              </p>
            </div>
          </div>

          {/* Step 4 */}
          <div className="rounded-2xl border border-white/80 bg-white/75 backdrop-blur-md p-5 flex flex-col justify-between space-y-3 shadow-xs">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-red-600">04</span>
                <Check className="h-4 w-4 text-emerald-600" />
              </div>
              <h3 className="text-sm font-bold text-stone-900 mt-2">
                Fixed & Rolling
              </h3>
              <p className="text-xs text-stone-700 mt-1 leading-relaxed">
                Problem solved on-spot. Approve the bill. Pay via UPI, card, or cash — only after satisfied.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/booking"
            className="inline-flex items-center gap-2 rounded-full bg-stone-900 hover:bg-black text-white px-7 py-3 text-xs font-bold transition-colors active:scale-95"
          >
            <span>Book Now →</span>
          </Link>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 9. WHAT CUSTOMERS SAY (AUTHENTIC GOOGLE REVIEWS)              */}
      {/* ============================================================== */}
      <section className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto text-left">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
            WHAT CUSTOMERS SAY
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-stone-950">
            Trusted by 30,000+ Delhi NCR Drivers.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {realReviews.map((rev, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-stone-300 bg-white p-6 flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center gap-1 text-amber-500 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="text-xs text-stone-800 leading-relaxed italic">
                  &ldquo;{rev.text}&rdquo;
                </p>
              </div>

              <div className="flex items-center gap-3 pt-3 border-t border-stone-200">
                <div className="h-8 w-8 rounded-full bg-stone-100 text-stone-900 flex items-center justify-center font-bold text-xs font-mono">
                  {rev.initials}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-stone-900 flex items-center gap-1">
                    <span>{rev.name}</span>
                    <span className="text-blue-600 text-[10px]">✓</span>
                  </h4>
                  <span className="text-[10px] text-stone-500 block font-mono">
                    {rev.role}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 10. SERVICE COVERAGE (DELHI NCR — EVERY CORNER COVERED)       */}
      {/* ============================================================== */}
      <section id="coverage" className="relative z-10 py-16 sm:py-24 px-2 sm:px-4 lg:px-6 max-w-6xl mx-auto text-left">
        <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md p-8 sm:p-12 shadow-xs">
          <div className="max-w-3xl">
            <span className="text-[11px] font-mono font-bold text-red-600 uppercase tracking-widest block mb-2">
              SERVICE COVERAGE
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-stone-950">
              Delhi NCR — Every Corner Covered.
            </h2>
            <p className="text-xs sm:text-sm text-stone-700 mt-2 leading-relaxed">
              500+ mechanics across the region. Expanding to top 20 Indian cities by 2028.
            </p>
          </div>

          <div className="mt-8 flex flex-wrap gap-2.5">
            {coverageAreas.map((area) => (
              <span
                key={area}
                className="inline-flex items-center gap-1 rounded-full bg-stone-100 border border-stone-200 px-3.5 py-1.5 text-xs font-bold text-stone-900"
              >
                <MapPin className="h-3 w-3 text-stone-600" />
                <span>{area}</span>
              </span>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t border-stone-200 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-2 text-stone-700 font-medium">
              <Globe className="h-4 w-4 text-stone-600" />
              <span>Expanding to Mumbai, Pune, Bangalore Soon</span>
            </div>
            <div className="flex items-center gap-4 font-mono text-[11px] text-stone-600">
              <span>HQ: Sector 75, Gurugram</span>
              <span>•</span>
              <span className="text-emerald-700 font-bold">Live 24×7</span>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 11. FINAL CTA SECTION (DRIVE WITH CONFIDENCE)                 */}
      {/* ============================================================== */}
      <section className="relative z-10 py-20 sm:py-28 px-2 sm:px-4 lg:px-6 max-w-4xl mx-auto text-center">
        {/* Centered Small Icon Squircle */}
        <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white border border-stone-300 text-stone-900 mb-6">
          <Zap className="h-5 w-5 text-stone-800" />
        </div>

        <h2 className="text-3xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-stone-950 max-w-2xl mx-auto leading-tight">
          Drive With Confidence. <br />
          <span className="text-red-600">Your Car. Our Problem. Always.</span>
        </h2>

        <p className="mt-4 text-sm text-stone-700 max-w-xl mx-auto leading-relaxed">
          India&apos;s most trusted car care platform is one call away. Emergency help in 20 minutes, AI diagnosis free, transparent pricing — always.
        </p>

        {/* Action Buttons with black text, no glow, no shadow */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <a
            href="tel:+919266961110"
            className="inline-flex items-center gap-2 rounded-full bg-white hover:bg-stone-100 text-stone-950 border border-stone-300 px-7 py-3 text-xs sm:text-sm font-bold transition-colors active:scale-95"
          >
            <Phone className="h-4 w-4 text-red-600" />
            <span>Call +91 9266961110</span>
          </a>
          <a
            href="https://wa.me/919266961110"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-full bg-white hover:bg-stone-100 text-stone-950 border border-stone-300 px-6 py-3 text-xs sm:text-sm font-bold transition-colors active:scale-95"
          >
            <MessageSquare className="h-4 w-4 text-stone-800" />
            <span>WhatsApp Us</span>
          </a>
          <Link
            href="/chat"
            className="btn-metal-shine inline-flex items-center gap-2 rounded-full px-6 py-3 text-xs sm:text-sm font-bold active:scale-95"
          >
            <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10 animate-pulse" />
            <span className="relative z-10">AI Diagnosis — Free</span>
          </Link>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 12. DEEP DARK CURVED FOOTER (FLAT MINIMALIST BORDER)          */}
      {/* ============================================================== */}
      <footer className="relative z-10 mt-12 rounded-t-[2.5rem] sm:rounded-t-[3.5rem] bg-[#0c0c0e] text-white pt-16 sm:pt-20 pb-12 px-6 sm:px-12 lg:px-16 border-t border-stone-800">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-10 lg:gap-16 pb-12 border-b border-stone-800 text-left">
          
          {/* Brand Info with clean removebg logo capsule */}
          <div className="md:col-span-5 space-y-4">
            <Link href="/" className="inline-block">
              <div className="bg-white px-3 py-1.5 rounded-full inline-flex items-center">
                <div className="relative h-6 w-28">
                  <Image
                    src="/brand-logo.png"
                    alt="Instant Mechanic"
                    fill
                    className="object-contain"
                  />
                </div>
              </div>
            </Link>
            <p className="text-xs text-stone-400 leading-relaxed max-w-sm">
              Building India&apos;s largest car care platform — instant roadside response, AI-powered diagnosis, and transparent repairs for every car owner in India.
            </p>
            {/* Social / Channel Tags */}
            <div className="flex items-center gap-3 text-stone-400 pt-2 text-xs font-mono">
              <span className="px-2 py-1 bg-white/5 rounded border border-white/10">IG</span>
              <span className="px-2 py-1 bg-white/5 rounded border border-white/10">in</span>
              <span className="px-2 py-1 bg-white/5 rounded border border-white/10">WA</span>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/30">Live 24×7</span>
            </div>
          </div>

          {/* Links Column 1: Platform */}
          <div className="md:col-span-2 space-y-3">
            <span className="text-[11px] font-mono font-bold tracking-widest text-stone-400 uppercase block">
              PLATFORM
            </span>
            <ul className="space-y-2 text-xs text-stone-400">
              <li>
                <a href="#services" className="hover:text-white transition-colors">
                  Car Services
                </a>
              </li>
              <li>
                <Link href="/chat" className="hover:text-white transition-colors">
                  AI Diagnosis
                </Link>
              </li>
              <li>
                <a href="#membership" className="hover:text-white transition-colors">
                  Membership Plans
                </a>
              </li>
              <li>
                <Link href="/booking" className="hover:text-white transition-colors">
                  Car Servicing
                </Link>
              </li>
            </ul>
          </div>

          {/* Links Column 2: Policies */}
          <div className="md:col-span-2 space-y-3">
            <span className="text-[11px] font-mono font-bold tracking-widest text-stone-400 uppercase block">
              POLICIES
            </span>
            <ul className="space-y-2 text-xs text-stone-400">
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Terms & Conditions
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Cancellation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Refund Policy
                </a>
              </li>
            </ul>
          </div>

          {/* Links Column 3: Contact */}
          <div className="md:col-span-3 space-y-3">
            <span className="text-[11px] font-mono font-bold tracking-widest text-stone-400 uppercase block">
              CONTACT
            </span>
            <div className="space-y-2 text-xs text-stone-400">
              <div>
                <span className="text-[10px] text-stone-500 block">Address</span>
                <span>Sector 75, Gurugram, Haryana</span>
              </div>
              <div>
                <span className="text-[10px] text-stone-500 block">Phone / WhatsApp</span>
                <a href="tel:+919266961110" className="text-red-400 font-mono font-bold hover:underline">
                  +91 9266961110
                </a>
              </div>
              <div>
                <span className="text-[10px] text-stone-500 block">Email</span>
                <a href="mailto:gordhan@instantmechanic.online" className="hover:underline">
                  gordhan@instantmechanic.online
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Legal Row */}
        <div className="max-w-7xl mx-auto pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-stone-500">
          <p>© 2024 Instant Mechanic. All rights reserved.</p>
          <div className="flex items-center gap-6 text-[11px]">
            <a href="#" className="hover:text-stone-300 transition-colors">Privacy</a>
            <a href="#" className="hover:text-stone-300 transition-colors">Terms</a>
            <a href="#" className="hover:text-stone-300 transition-colors">Refund</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
