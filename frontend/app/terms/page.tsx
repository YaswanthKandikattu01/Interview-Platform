import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "Terms of Service | MockInterview.in",
  description: "Terms and conditions governing mock interview bookings and platform use.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12 px-4 sm:px-6 lg:px-8 transition-colors">
      <div className="max-w-4xl mx-auto bg-white dark:bg-slate-900 p-8 sm:p-12 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-8 transition-colors">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-400">
            <ShieldCheck className="w-4 h-4" />
            <span>Legal Compliance</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">Terms of Service</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Last Updated: October 2026</p>
        </div>

        <div className="prose prose-slate dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 space-y-6 leading-relaxed">
          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">1. Nature of the Service</h2>
            <p>
              MockInterview.in provides human-led, one-on-one technical mock interview sessions and resume reviews conducted by an experienced
              software engineer. We do NOT use AI interviewers or automated bots for evaluations.
              Mock interviews are intended strictly for educational and preparation purposes and do not constitute an offer of employment or a guarantee of job placement.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">2. Pricing & Programs</h2>
            <p>
              Program fees are clearly displayed before payment:
              - Technical Mock Interviews (DSA, AI, Full Stack, Frontend, Backend): ₹199 flat fee (45–60 minutes session).
              - System Design Intensive: ₹499 flat fee (2 Hours / 120 minutes deep dive).
              - Resume Review & Strategy: ₹119 flat fee (comprehensive line-by-line review).
              Payments are processed securely in Indian Rupees (INR) via Razorpay. We do not store card numbers or UPI PINs on our servers.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">3. Scheduling & Same-Day Contact SLA</h2>
            <p>
              Candidates do not select an interview date or time on the website during booking. Instead, the interviewer personally
              reaches out to the candidate via email on the same calendar day (Asia/Kolkata timezone) to coordinate a mutually convenient date and time.
              For bookings made after 8:00 PM IST, the personal contact window extends until 12:00 PM (noon) IST the following calendar day.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">4. Candidate Conduct & Equipment</h2>
            <p>
              Candidates must join the scheduled session using a functional computer with a working webcam, microphone, and stable internet connection.
              Sessions are conducted via Google Meet or Zoom.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">5. Governing Law</h2>
            <p>
              These Terms are governed by and construed in accordance with the laws of India. Any disputes arising under these Terms shall be subject to the jurisdiction of the competent courts of India.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
