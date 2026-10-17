import Link from "next/link";
import { ArrowLeft, RotateCcw, CheckCircle2, AlertTriangle } from "lucide-react";

export const metadata = {
  title: "Cancellation & Refund Policy | MockInterview.in",
  description: "Transparent refund guarantees, cancellation policies, and same-day contact SLA commitments.",
};

export default function RefundPolicyPage() {
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
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
            <RotateCcw className="w-4 h-4" />
            <span>Fair & Transparent Guarantee</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">Cancellation & Refund Policy</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">100% Protection Guarantee for Technical Candidates</p>
        </div>

        <div className="prose prose-slate dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 space-y-6 leading-relaxed">
          <section className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 p-5 rounded-xl">
            <h2 className="text-base font-bold text-emerald-900 dark:text-emerald-300 mt-0 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-700 dark:text-emerald-400" />
              <span>Same-Day Contact Guarantee</span>
            </h2>
            <p className="text-emerald-800 dark:text-emerald-200 text-xs mt-1 mb-0">
              When you book a mock interview or resume review, our interviewer guarantees personal email contact on the same calendar day
              (or before 12:00 PM next day for bookings completed after 8:00 PM IST).
              If we ever fail to reach out within this window, you are entitled to an immediate <strong>100% full refund</strong> upon request.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">1. Candidate Rescheduling</h2>
            <p>
              We understand emergencies happen. You may reschedule your interview date and time without any penalty by emailing the interviewer at least
              <strong> 12 hours</strong> prior to your scheduled session. The interviewer will coordinate an alternative slot.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">2. Candidate Cancellation & Refunds</h2>
            <p>
              If you decide to cancel your booking before the interview or review has been conducted:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Prior to mutual scheduling confirmation:</strong> 100% full refund.</li>
              <li><strong>More than 12 hours before scheduled slot:</strong> 100% full refund.</li>
              <li><strong>Less than 12 hours or no-show:</strong> Due to slot reservation, refunds are processed at the interviewer&apos;s discretion or rescheduled.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">3. Interviewer Cancellation</h2>
            <p>
              If the interviewer is unable to conduct the session due to unforeseen technical failure or emergency, you will be offered
              the choice between immediate priority rescheduling or an instant 100% full refund.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">4. Refund Processing Timelines</h2>
            <p>
              Approved refunds are initiated through Razorpay immediately.
              Depending on your bank or original payment method (UPI, Netbanking, Credit/Debit Card), the funds will credit your account within
              <strong> 5 to 7 business days</strong>.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">5. How to Request a Refund</h2>
            <p>
              Simply email our support team at{" "}
              <a href="mailto:support@mockinterviews.dev" className="text-sky-600 dark:text-sky-400 font-medium underline">
                support@mockinterviews.dev
              </a>{" "}
              quoting your <strong>Booking Reference (MOCK-YYMM-XXXX)</strong> and Razorpay payment reference.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
