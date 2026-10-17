import Link from "next/link";
import { ArrowLeft, ShieldCheck, Lock } from "lucide-react";

export const metadata = {
  title: "Privacy Policy | MockInterview.in",
  description: "Privacy policy detailing data collection, resume security, and storage protections.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12 px-4 sm:px-6 lg:px-8 transition-colors">
      <div className="max-w-4xl mx-auto bg-white dark:bg-slate-900 p-8 sm:p-12 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-400">
            <Lock className="w-4 h-4" />
            <span>Data Protection & Privacy</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">Privacy Policy</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Effective Date: October 2026</p>
        </div>

        <div className="prose prose-slate dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 space-y-6 leading-relaxed">
          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">1. Information We Collect</h2>
            <p>
              When you book a mock interview or resume review, we collect:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Contact Information:</strong> Full name, email address, phone number (optional).</li>
              <li><strong>Candidate Context:</strong> Topic suggestions, target companies, or specific notes for the interviewer.</li>
              <li><strong>Documents:</strong> Uploaded resumes (PDF/DOCX) securely validated.</li>
              <li><strong>Payment Metadata:</strong> Razorpay order ID and payment verification status (no card numbers stored).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">2. Resume Security & Document Handling</h2>
            <p>
              Uploaded resumes are inspected using strict magic-byte verification (rejecting executable or script payloads)
              and stored with randomized UUID filenames outside public web directories. Only the interviewer and the candidate
              themselves have access to uploaded documents through authenticated, anti-IDOR protected endpoints.
              We do NOT sell, lease, or share candidate resumes with recruitment agencies or third parties.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">3. Authentication & Security</h2>
            <p>
              We protect sessions using industry-standard cryptography, short-lived JWT access tokens,
              cryptographically secured HttpOnly cookies with SameSite attributes, and Double Submit CSRF defense tokens.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">4. Third-Party Integrations</h2>
            <p>
              We integrate with trusted service providers:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Razorpay:</strong> To process secure payments in Indian Rupees (INR).</li>
              <li><strong>Resend:</strong> To transmit automated booking confirmations and interview calendar invitations.</li>
              <li><strong>Supabase:</strong> For managed PostgreSQL database hosting.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">5. Data Retention & Deletion</h2>
            <p>
              Candidates may request deletion of their records and uploaded documents at any time by contacting{" "}
              <a href="mailto:support@mockinterviews.dev" className="text-sky-600 dark:text-sky-400 font-medium underline">
                support@mockinterviews.dev
              </a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
