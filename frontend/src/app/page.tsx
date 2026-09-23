'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Wrench,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Sparkles,
  ArrowRight,
  Car,
  Activity
} from 'lucide-react';

const HERO_SLIDES = [
  {
    id: 1,
    tag: 'गाड़ी खराब, मैकेनिक तैयार',
    headline: '« INSTANT MECHANIC »',
    description:
      'कार में कोई भी खराबी? अजीब आवाज़, वाइब्रेशन या वार्निंग लाइट—हमारा AI तकनीक से लैस सिस्टम तुरंत असली वजह पहचानेगा और आपके पास वेरिफाइड मैकेनिक भेजेगा।',
    buttonText: 'START INSTANT DIAGNOSIS 🔧',
    badgeText: '25-Year ASE Master Tech Intelligence',
  },
  {
    id: 2,
    tag: 'ध्वनि और फोटो से जांच',
    headline: '« SOUND & VISION AI »',
    description:
      'इंजन की खड़खड़ाहट या ब्रेक की चीखती आवाज़ रिकॉर्ड करें। हमारा AI ऑडियो फ्रीक्वेंसी और विज़ुअल फोटो का विश्लेषण करके सही फॉल्ट बताता है।',
    buttonText: 'RECORD CAR SOUND 🎙️',
    badgeText: 'Acoustic Sound Frequency Analyzer',
  },
  {
    id: 3,
    tag: 'घर बैठे मैकेनिक सेवा',
    headline: '« DOORSTEP SERVICE »',
    description:
      'डायग्नोसिस के बाद 1-क्लिक में प्रमाणित मोबाइल मैकेनिक बुक करें। ट्रांसपेरेंट रेट्स और 100% ओरिजिनल पार्ट्स की गारंटी।',
    buttonText: 'SCHEDULE REPAIR NOW 📅',
    badgeText: 'Doorstep Mobile Mechanic Dispatch',
  },
];

const COMMON_ISSUES = [
  {
    title: 'Clicking noise when turning',
    vehicle: 'Hyundai Creta',
    query: 'My car is making a clicking noise when I turn left.',
    badge: 'CV Joint / Axle',
    severity: 'Medium',
  },
  {
    title: 'Squealing / grinding brakes',
    vehicle: 'Maruti Swift',
    query: 'My brakes are squealing loudly whenever I press the pedal.',
    badge: 'Brake Pads / Rotors',
    severity: 'High',
  },
  {
    title: "Engine won't crank / rapid clicking",
    vehicle: 'Tata Nexon',
    query: "My car won't start. When I turn the key, it makes a rapid clicking sound.",
    badge: 'Battery / Alternator',
    severity: 'Medium',
  },
  {
    title: 'Engine overheating & steam',
    vehicle: 'Honda City',
    query: 'The engine temperature gauge is in the red and I see steam under the hood.',
    badge: 'Cooling System',
    severity: 'High',
  },
  {
    title: 'Steering vibration at 80 km/h',
    vehicle: 'Mahindra XUV700',
    query: 'My steering wheel shakes violently when driving around 80 to 100 km/h.',
    badge: 'Wheel Balancing',
    severity: 'Medium',
  },
  {
    title: 'Check Engine light blinking',
    vehicle: 'Toyota Innova',
    query: 'The check engine light is flashing and the engine is shaking and losing power.',
    badge: 'Engine Misfire',
    severity: 'High',
  },
];

const OEM_BRANDS = [
  'Hyundai', 'Maruti Suzuki', 'Tata Motors', 'Mahindra', 'Toyota', 'Honda', 'Kia', 'Volkswagen', 'Skoda', 'MG Motors'
];

export default function HomePage() {
  const router = useRouter();
  const [currentSlide, setCurrentSlide] = useState(0);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % HERO_SLIDES.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + HERO_SLIDES.length) % HERO_SLIDES.length);
  };

  const handleQuickDiagnose = (query: string) => {
    sessionStorage.setItem('initial_mechanic_query', query);
    router.push('/chat');
  };

  const slide = HERO_SLIDES[currentSlide];

  return (
    <div className="relative min-h-screen bg-desk-texture text-stone-900 pb-20 overflow-hidden">
      {/* ============================================================== */}
      {/* 1. HERO SECTION (INSPIRED BY REFERENCE DESIGN)                 */}
      {/* ============================================================== */}
      <section className="relative pt-6 pb-12 sm:pt-10 sm:pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative">
          
          {/* Desk Props - Left Side (Job Card / Clipboard Document) */}
          <div className="hidden xl:block absolute left-2 top-8 w-60 rotate-[-8deg] pointer-events-none select-none drop-shadow-xl z-10 transition-transform hover:rotate-[-5deg]">
            <div className="rounded-2xl border border-stone-300 bg-white p-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-stone-200 pb-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-orange-600">
                  Instant Mechanic Job Card
                </span>
                <span className="text-[9px] font-mono text-stone-400">#IM-2026</span>
              </div>
              <div className="space-y-1.5 text-[11px] text-stone-600">
                <div className="flex justify-between">
                  <span className="text-stone-400">Vehicle:</span>
                  <span className="font-semibold text-stone-800">Hyundai Creta</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-400">Symptom:</span>
                  <span className="text-stone-800">CV Joint Click</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-400">Status:</span>
                  <span className="font-bold text-emerald-600">Verified</span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-stone-100 flex items-center gap-1.5 text-[10px] text-stone-500">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                <span>OEM Spec 40-Point Check</span>
              </div>
            </div>
            {/* Pen prop */}
            <div className="h-2 w-32 bg-gradient-to-r from-stone-800 via-stone-700 to-amber-500 rounded-full mt-3 ml-8 shadow-md" />
          </div>

          {/* Desk Props - Right Side (Laptop & OBD Diagnostic Tool) */}
          <div className="hidden xl:block absolute right-2 top-8 w-60 rotate-[6deg] pointer-events-none select-none drop-shadow-xl z-10 transition-transform hover:rotate-[3deg]">
            <div className="rounded-2xl border border-stone-800 bg-stone-900 p-4 shadow-2xl text-stone-200">
              <div className="flex items-center gap-2 border-b border-stone-800 pb-2 mb-2">
                <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-amber-400">
                  OBD-II LIVE TELEMETRY
                </span>
              </div>
              <div className="space-y-1 font-mono text-[10px] text-stone-400">
                <p>&gt; Scanning CAN-BUS...</p>
                <p className="text-amber-300">&gt; DTC: P0300 (Random Misfire)</p>
                <p className="text-emerald-400">&gt; Gemini AI: Isolated</p>
              </div>
              <div className="mt-3 rounded-lg bg-stone-950 p-2 border border-stone-800 flex items-center justify-between text-[10px]">
                <span className="text-stone-400">Sensor Rate</span>
                <span className="font-bold text-white">60 FPS</span>
              </div>
            </div>
            {/* Car key / Fob prop */}
            <div className="h-10 w-16 bg-stone-950 border border-stone-700 rounded-xl mt-3 ml-12 shadow-lg flex items-center justify-center text-amber-400">
              <Car className="h-5 w-5" />
            </div>
          </div>

          {/* Centerpiece Container with Carousel Arrows */}
          <div className="relative mx-auto max-w-3xl">
            {/* Carousel Arrow Left */}
            <button
              onClick={prevSlide}
              className="absolute left-[-20px] sm:left-[-40px] top-1/2 -translate-y-1/2 z-30 flex h-11 w-11 items-center justify-center rounded-full bg-white border border-stone-300 text-stone-700 shadow-lg transition-transform hover:scale-110 active:scale-95"
              aria-label="Previous Slide"
            >
              <ChevronLeft className="h-6 w-6" />
            </button>

            {/* Carousel Arrow Right */}
            <button
              onClick={nextSlide}
              className="absolute right-[-20px] sm:right-[-40px] top-1/2 -translate-y-1/2 z-30 flex h-11 w-11 items-center justify-center rounded-full bg-white border border-stone-300 text-stone-700 shadow-lg transition-transform hover:scale-110 active:scale-95"
              aria-label="Next Slide"
            >
              <ChevronRight className="h-6 w-6" />
            </button>

            {/* The Main Illustrated Center Banner (matching reference style) */}
            <div className="relative rounded-3xl overflow-hidden torn-paper-edge border-4 border-white shadow-2xl bg-gradient-to-b from-orange-500 via-orange-600 to-amber-600 text-white p-6 sm:p-10 text-center">
              
              {/* Badge at top */}
              <div className="inline-flex items-center gap-1.5 rounded-full bg-black/30 backdrop-blur-md px-3.5 py-1 text-xs font-bold text-amber-200 border border-amber-300/30 mb-4">
                <Sparkles className="h-3.5 w-3.5" />
                <span>{slide.tag}</span>
              </div>

              {/* Editorial Headline with quotation marks */}
              <h1 className="text-3xl sm:text-5xl font-black tracking-tight drop-shadow-md uppercase">
                {slide.headline}
              </h1>

              {/* Hero Image Art inside the banner */}
              <div className="relative mx-auto my-4 h-44 sm:h-56 w-full max-w-sm">
                <Image
                  src="/hero-image.png"
                  alt="गाड़ी खराब, मैकेनिक तैयार"
                  fill
                  className="object-contain drop-shadow-xl"
                  priority
                />
              </div>

              {/* Subtitle Description */}
              <p className="mx-auto max-w-lg text-xs sm:text-sm text-orange-50 leading-relaxed font-medium drop-shadow">
                {slide.description}
              </p>

              {/* The Turquoise/Cyan CTA Button (exact color & style as in the reference!) */}
              <div className="mt-6 flex justify-center">
                <Link
                  href="/chat"
                  className="inline-flex items-center gap-2 rounded-full bg-[#14b8a6] hover:bg-[#0d9488] px-7 py-3 text-xs sm:text-sm font-black tracking-wider text-stone-950 uppercase shadow-xl transition-all hover:scale-105 active:scale-95 border-2 border-white/60"
                >
                  <span>{slide.buttonText}</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {/* Slide Indicators */}
              <div className="mt-5 flex justify-center gap-2">
                {HERO_SLIDES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentSlide(i)}
                    className={`h-2 rounded-full transition-all ${
                      i === currentSlide ? 'w-6 bg-white' : 'w-2 bg-white/40'
                    }`}
                    aria-label={`Go to slide ${i + 1}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 2. FLOWING SCHEMATIC LINE & FEATURES (LIKE REFERENCE DIAGRAM)  */}
      {/* ============================================================== */}
      <section className="relative py-12">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          
          {/* Centered Computer Mouse with flowing cord */}
          <div className="flex flex-col items-center justify-center mb-6">
            <div className="h-14 w-9 rounded-2xl border-2 border-stone-400 bg-white shadow-md flex items-start justify-center pt-2">
              <div className="h-3 w-1 bg-stone-700 rounded-full" />
            </div>
            {/* Flowing cable SVG */}
            <svg className="w-full max-w-md h-12" viewBox="0 0 400 48" fill="none">
              <path
                d="M200,0 C200,24 200,24 200,48"
                stroke="#a8a29e"
                strokeWidth="2"
                strokeDasharray="4 4"
              />
            </svg>
          </div>

          {/* Narrative statement block */}
          <div className="max-w-2xl mx-auto space-y-2 mb-10">
            <p className="text-base sm:text-lg font-bold text-stone-800">
              Instant Mechanic AI brings master garage precision directly to your fingertips.
            </p>
            <p className="text-xs sm:text-sm text-stone-500 leading-relaxed">
              We eliminate guesswork and dealership overcharging by combining deterministic automotive logic
              with Gemini AI reasoning to pinpoint mechanical faults in seconds.
            </p>
          </div>

          {/* Heading */}
          <div className="mb-10">
            <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
              Diagnostic Precision Workflow
            </span>
            <h2 className="text-xl sm:text-2xl font-black text-stone-900 mt-1">
              5 Pillars of the Instant Mechanic Guarantee
            </h2>
          </div>

          {/* Connected Circular Nodes (matching reference design layout) */}
          <div className="relative py-6">
            {/* Dotted connecting wave line */}
            <div className="hidden md:block absolute top-1/2 left-4 right-4 -translate-y-1/2 h-0.5 border-t-2 border-dashed border-stone-300 z-0" />

            <div className="grid grid-cols-2 md:grid-cols-5 gap-6 relative z-10">
              {/* Node 1 */}
              <div className="flex flex-col items-center text-center group">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-stone-900 text-white shadow-lg border-4 border-white transition-transform group-hover:scale-110">
                  <Activity className="h-6 w-6 text-amber-400" />
                </div>
                <h3 className="mt-3 text-xs font-bold text-stone-800">Acoustic Analysis</h3>
                <p className="text-[11px] text-stone-500 mt-0.5">Sound & frequency inspection</p>
              </div>

              {/* Node 2 */}
              <div className="flex flex-col items-center text-center group">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-orange-500 text-white shadow-lg border-4 border-white transition-transform group-hover:scale-110">
                  <Wrench className="h-6 w-6 text-white" />
                </div>
                <h3 className="mt-3 text-xs font-bold text-stone-800">Fault Isolation</h3>
                <p className="text-[11px] text-stone-500 mt-0.5">Exact root-cause pinpointing</p>
              </div>

              {/* Node 3 (Center Star / Core) */}
              <div className="flex flex-col items-center text-center group col-span-2 md:col-span-1">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-stone-950 font-black shadow-xl border-4 border-white transition-transform group-hover:scale-110">
                  <span className="text-xl font-mono">₹ Fair</span>
                </div>
                <h3 className="mt-3 text-xs font-bold text-stone-800">Transparent Pricing</h3>
                <p className="text-[11px] text-stone-500 mt-0.5">Zero surprise charges</p>
              </div>

              {/* Node 4 */}
              <div className="flex flex-col items-center text-center group">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-stone-900 text-white shadow-lg border-4 border-white transition-transform group-hover:scale-110">
                  <ShieldCheck className="h-6 w-6 text-amber-400" />
                </div>
                <h3 className="mt-3 text-xs font-bold text-stone-800">Verified Mechanics</h3>
                <p className="text-[11px] text-stone-500 mt-0.5">Vetted background checks</p>
              </div>

              {/* Node 5 */}
              <div className="flex flex-col items-center text-center group">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-orange-500 text-white shadow-lg border-4 border-white transition-transform group-hover:scale-110">
                  <Calendar className="h-6 w-6 text-white" />
                </div>
                <h3 className="mt-3 text-xs font-bold text-stone-800">Doorstep Dispatch</h3>
                <p className="text-[11px] text-stone-500 mt-0.5">30-min mobile arrival</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 3. CENTRAL PHONE SHOWCASE (LIKE SMARTPHONE IN REFERENCE)       */}
      {/* ============================================================== */}
      <section className="relative py-12">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 text-center">
          
          {/* Wave line traversing behind the phone */}
          <div className="relative py-6">
            <svg className="w-full h-24 hidden sm:block opacity-40" viewBox="0 0 1000 100" fill="none">
              <path
                d="M0,50 Q250,0 500,50 T1000,50"
                stroke="#f97316"
                strokeWidth="3"
                className="animate-flow-line"
              />
            </svg>

            {/* Smartphone Mockup */}
            <div className="relative mx-auto w-full max-w-sm sm:max-w-md rounded-[2.5rem] border-8 border-stone-200 bg-white p-3 shadow-2xl drop-shadow-2xl">
              {/* Notch / Speaker */}
              <div className="mx-auto h-4 w-28 bg-stone-200 rounded-full mb-2" />

              {/* Phone Screen */}
              <div className="rounded-2xl border border-stone-100 bg-stone-900 p-4 text-left text-white shadow-inner">
                {/* Header */}
                <div className="flex items-center justify-between pb-2 border-b border-stone-800">
                  <span className="text-[10px] font-bold text-amber-400">INSTANT MECHANIC AI</span>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-400 font-mono px-2 py-0.5 rounded-full">
                    ● Live Scan
                  </span>
                </div>

                {/* Metric Graph preview */}
                <div className="my-3 grid grid-cols-2 gap-2">
                  <div className="rounded-xl bg-stone-800/80 p-2.5">
                    <span className="text-[10px] text-stone-400 block">AI Accuracy</span>
                    <span className="text-lg font-black text-amber-400">98.4%</span>
                  </div>
                  <div className="rounded-xl bg-stone-800/80 p-2.5">
                    <span className="text-[10px] text-stone-400 block">ETA Dispatch</span>
                    <span className="text-lg font-black text-emerald-400">25 Mins</span>
                  </div>
                </div>

                {/* Diagnosis Preview Card */}
                <div className="rounded-xl bg-orange-500/10 border border-orange-500/30 p-3 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase text-orange-400">
                      Isolated Fault
                    </span>
                    <span className="text-[9px] font-bold bg-amber-500 text-stone-950 px-1.5 py-0.2 rounded">
                      MEDIUM SEVERITY
                    </span>
                  </div>
                  <p className="text-xs font-bold text-white">
                    CV Joint / Front Axle Wear
                  </p>
                  <p className="text-[10px] text-stone-300">
                    Recommended: CV Joint & Axle Inspection
                  </p>
                </div>

                {/* Phone CTA */}
                <Link
                  href="/chat"
                  className="mt-3 block w-full text-center rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 py-2.5 text-xs font-bold text-stone-950 shadow-md transition-transform active:scale-95"
                >
                  Book Doorstep Mechanic 🔧
                </Link>
              </div>

              {/* Home bar */}
              <div className="mx-auto h-1 w-24 bg-stone-300 rounded-full mt-3" />
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 4. OEM & BRAND TRUST ROW (LIKE BANK LOGOS IN REFERENCE)         */}
      {/* ============================================================== */}
      <section className="mx-auto max-w-6xl px-4 py-8 border-y border-stone-200">
        <div className="text-center mb-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400">
            Works with All Leading Vehicle Manufacturers in India & Globally
          </span>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-6">
          {OEM_BRANDS.map((brand, idx) => (
            <span
              key={idx}
              className="rounded-full border border-stone-300 bg-white px-3.5 py-1 text-xs font-semibold text-stone-700 shadow-sm transition-colors hover:border-orange-500 hover:text-orange-600"
            >
              {brand}
            </span>
          ))}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 5. QUICK COMMON ISSUE TROUBLESHOOTER TILES                     */}
      {/* ============================================================== */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
              One-Click Symptom Launcher
            </span>
            <h2 className="text-2xl font-black text-stone-900 mt-1">
              Test Common Vehicle Issues
            </h2>
            <p className="text-xs sm:text-sm text-stone-500 mt-1">
              Select any scenario below to immediately trigger the AI mechanic diagnostic dialogue.
            </p>
          </div>

          <Link
            href="/chat"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-orange-600 hover:text-orange-700"
          >
            <span>Custom Symptom? Type Your Own</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {COMMON_ISSUES.map((issue, idx) => (
            <div
              key={idx}
              onClick={() => handleQuickDiagnose(issue.query)}
              className="group cursor-pointer rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition-all hover:border-orange-500 hover:shadow-md hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="rounded-full bg-orange-50 px-2.5 py-0.5 text-[11px] font-bold text-orange-600 border border-orange-200">
                  {issue.badge}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    issue.severity === 'High'
                      ? 'bg-rose-100 text-rose-700'
                      : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {issue.severity} Severity
                </span>
              </div>

              <h3 className="text-sm sm:text-base font-bold text-stone-900 group-hover:text-orange-600 transition-colors">
                {issue.title}
              </h3>
              <p className="mt-2 text-xs text-stone-500 line-clamp-2 italic">
                &quot;{issue.query}&quot;
              </p>

              <div className="mt-4 flex items-center justify-between pt-3 border-t border-stone-100 text-xs">
                <span className="text-stone-400 font-mono">Example: {issue.vehicle}</span>
                <span className="flex items-center gap-1 font-bold text-orange-600 group-hover:translate-x-1 transition-transform">
                  Diagnose <ArrowRight className="h-3.5 w-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 6. BOTTOM CALL TO ACTION                                      */}
      {/* ============================================================== */}
      <section className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-3xl border-2 border-stone-900 bg-stone-900 p-8 sm:p-12 text-center text-white shadow-2xl relative overflow-hidden">
          <div className="relative z-10 space-y-4">
            <span className="inline-block rounded-full bg-amber-400/20 px-3 py-1 text-xs font-bold text-amber-300">
              गाड़ी कभी भी, कहीं भी रुके—मैकेनिक हाज़िर!
            </span>
            <h2 className="text-2xl sm:text-4xl font-black">
              Ready to Troubleshoot Your Car?
            </h2>
            <p className="mx-auto max-w-md text-xs sm:text-sm text-stone-300">
              Get an instant AI diagnosis with zero sign-up friction. Describe the issue or record audio now.
            </p>
            <div className="pt-2">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-amber-500 px-8 py-3.5 text-sm font-black text-stone-950 shadow-xl transition-all hover:scale-105 active:scale-95"
              >
                <Wrench className="h-4 w-4" />
                <span>START FREE DIAGNOSIS NOW</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
