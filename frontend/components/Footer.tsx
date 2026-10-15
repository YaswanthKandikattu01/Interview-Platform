import Link from "next/link";
import { Mail, Clock, ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full bg-slate-900 text-slate-400 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-white text-slate-900 flex items-center justify-center font-bold text-sm">
                M
              </div>
              <span className="font-extrabold text-white text-lg tracking-tight">
                MockInterview<span className="text-sky-400">.in</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed">
              India&apos;s premium human-led mock interview platform. 100% live technical interviews with a senior software engineer across System Design, DSA, AI, Full Stack, Frontend, and Backend.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-400 pt-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <span>Operating in Asia/Kolkata (IST) • Same-Day Scheduling Contact</span>
            </div>
          </div>

          {/* Interview Categories */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Categories
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li><Link href="/book/system-design" className="hover:text-white transition-colors">System Design (₹199)</Link></li>
              <li><Link href="/book/dsa" className="hover:text-white transition-colors">DSA & Algorithms (₹199)</Link></li>
              <li><Link href="/book/ai-engineer" className="hover:text-white transition-colors">AI Engineer (₹199)</Link></li>
              <li><Link href="/book/full-stack" className="hover:text-white transition-colors">Full Stack (₹199)</Link></li>
              <li><Link href="/book/frontend" className="hover:text-white transition-colors">Frontend (₹199)</Link></li>
              <li><Link href="/book/backend" className="hover:text-white transition-colors">Backend (₹199)</Link></li>
            </ul>
          </div>

          {/* Legal & Support */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Trust & Support
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li><Link href="/#faqs" className="hover:text-white transition-colors">FAQs & SLA Cutoff</Link></li>
              <li><a href="mailto:support@mockinterviews.dev" className="inline-flex items-center gap-1.5 hover:text-white transition-colors"><Mail className="w-3.5 h-3.5 text-sky-400" /> support@mockinterviews.dev</a></li>
              <li className="pt-2 text-xs text-slate-400">Razorpay Verified 19,900 Paise (₹199)</li>
              <li className="text-xs text-slate-400">45–60 Minutes Session Guarantee</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} MockInterview.in. All rights reserved.</p>
          <div className="flex gap-6">
            <span>Terms of Service</span>
            <span>Privacy Policy</span>
            <span>Cancellation & Refund Policy</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
