import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "Terms of Service | MockInterview.in",
  description: "Terms and conditions governing mock interview bookings and platform use.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white p-8 sm:p-12 rounded-2xl border border-slate-200 shadow-sm space-y-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700">
            <ShieldCheck className="w-4 h-4" />
            <span>Legal Compliance</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 mt-2">Terms of Service</h1>
          <p className="text-sm text-slate-500 mt-1">Last Updated: October 2026</p>
        </div>

        <div className="prose prose-slate max-w-none text-sm text-slate-700 space-y-6 leading-relaxed">
          <section>
            <h2 className="text-lg font-bold text-slate-900">1. Nature of the Service</h2>
            <p>
              MockInterview.in provides human-led, one-on-one technical mock interview sessions conducted by an experienced
              software engineer. We do NOT use AI interviewers or automated bots for mock interview evaluations.
              Mock interviews are intended strictly for educational and preparation purposes and do not constitute an offer of employment or a guarantee of job placement.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900">2. Pricing & Payments</h2>
            <p>
              Each mock interview session is priced at exactly ₹199 (19,900 paise). The session duration is advertised as 45–60 minutes.
              Payments are processed securely in Indian Rupees (INR) via Razorpay. We do not store full credit/debit card numbers or UPI PINs on our servers.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900">3. Scheduling & Same-Day Contact SLA</h2>
            <p>
              Candidates do not select an interview date or time on the website during booking. Instead, the interviewer personally
              reaches out to the candidate via email on the same calendar day (Asia/Kolkata timezone) to coordinate a mutually convenient date and time.
              For bookings made after 8:00 PM IST, the personal contact window extends until 12:00 PM (noon) IST the following calendar day.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900">4. Candidate Conduct & Equipment</h2>
            <p>
              Candidates must join the scheduled session using a functional desktop/laptop computer with a working webcam, microphone, and stable high-speed internet connection.
              Sessions will be conducted over Google Meet or Zoom. Recording of sessions without explicit mutual consent is prohibited.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900">5. Limitation of Liability</h2>
            <p>
              In no event shall MockInterview.in or its interviewer be liable for any indirect, incidental, or consequential damages arising out of your mock interview session.
              Total liability under these terms is strictly limited to the amount paid for the session (₹199).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-slate-900">6. Contact Information</h2>
            <p>
              If you have any questions about these Terms, please contact us at{" "}
              <a href="mailto:support@mockinterviews.dev" className="text-sky-600 font-medium underline">
                support@mockinterviews.dev
              </a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
