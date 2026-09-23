import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Navbar from "@/components/Navbar";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Instant Mechanic — AI Car Diagnostic & Repair",
  description: "Diagnose vehicle troubles using AI and book verified mobile and garage auto mechanics instantly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-neutral-950 text-neutral-100 antialiased flex flex-col font-sans`}
      >
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-neutral-900 bg-neutral-950 py-6 text-center text-xs text-neutral-500">
          <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-neutral-400">Instant Mechanic</span>
              <span>• गाड़ी खराब, मैकेनिक तैयार</span>
            </div>
            <p>© {new Date().getFullYear()} Instant Mechanic. AI Diagnostic Engine.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
