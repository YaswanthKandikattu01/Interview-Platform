"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X, ArrowRight, User as UserIcon } from "lucide-react";
import { apiClient } from "@/services/api";
import { User } from "@/types/auth";
import ThemeToggle from "@/components/ThemeToggle";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    apiClient<{ user: User }>("/api/v1/auth/me")
      .then((data) => setUser(data.user))
      .catch(() => setUser(null));
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800/80 bg-white/95 dark:bg-slate-950/95 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-slate-900 dark:bg-sky-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
            M
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-slate-900 dark:text-white tracking-tight text-lg leading-none">
              MockInterview<span className="text-sky-600 dark:text-sky-400">.in</span>
            </span>
            <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 tracking-wider uppercase mt-0.5">
              Human-Led Tech Prep
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          <Link
            href="/#categories"
            className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            Categories
          </Link>
          <Link
            href="/#pricing"
            className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            Plans & Pricing
          </Link>
          <Link
            href="/#how-it-works"
            className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            How It Works
          </Link>
          <Link
            href="/#faqs"
            className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            FAQs
          </Link>
        </nav>

        {/* Desktop CTA / Auth / Theme Toggle */}
        <div className="hidden md:flex items-center gap-3">
          <ThemeToggle />

          {user ? (
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 px-4 py-2 rounded-lg transition-colors"
              >
                <UserIcon className="w-4 h-4 text-slate-600 dark:text-slate-300" />
                <span>{user.full_name}</span>
              </Link>
            </div>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-3 py-2"
              >
                Log In
              </Link>
              <Link
                href="/#categories"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 px-4 py-2 rounded-lg shadow-sm transition-all"
              >
                <span>Book Session</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </>
          )}
        </div>

        {/* Mobile Actions: Theme Toggle & Hamburger */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 pt-2 pb-6 space-y-3">
          <Link
            href="/#categories"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-base font-medium text-slate-700 dark:text-slate-200 py-2 hover:text-sky-600 dark:hover:text-sky-400"
          >
            Categories
          </Link>
          <Link
            href="/#pricing"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-base font-medium text-slate-700 dark:text-slate-200 py-2 hover:text-sky-600 dark:hover:text-sky-400"
          >
            Plans & Pricing
          </Link>
          <Link
            href="/#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-base font-medium text-slate-700 dark:text-slate-200 py-2 hover:text-sky-600 dark:hover:text-sky-400"
          >
            How It Works
          </Link>
          <Link
            href="/#faqs"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-base font-medium text-slate-700 dark:text-slate-200 py-2 hover:text-sky-600 dark:hover:text-sky-400"
          >
            FAQs
          </Link>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-2">
            {user ? (
              <Link
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 font-semibold text-slate-800 dark:text-slate-100 bg-slate-100 dark:bg-slate-800 rounded-lg"
              >
                My Dashboard ({user.full_name})
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2 text-slate-700 dark:text-slate-200 font-medium"
                >
                  Log In
                </Link>
                <Link
                  href="/#categories"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 font-semibold text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 rounded-lg shadow-sm"
                >
                  Book Session
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
