import Link from "next/link";
import { CheckCircle2, ShieldCheck, Clock, Award } from "lucide-react";

export default function HomePage() {
  return (
    <main className="flex-1 flex flex-col justify-center items-center px-4 py-16 sm:px-6 lg:px-8 text-center max-w-5xl mx-auto">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 border border-amber-200 text-amber-900 mb-6">
        <Award className="w-3.5 h-3.5 text-amber-600" />
        <span>100% Human-Led Technical Mock Interviews • ₹199 Flat</span>
      </div>

      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 mb-6">
        Prepare Smarter. <span className="text-sky-600">Perform Better.</span>
      </h1>

      <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mb-10 leading-relaxed">
        Live 45–60 minute technical mock interviews with a senior engineer. Gain actionable, candid feedback on System Design, DSA, AI Engineering, Full Stack, Frontend, or Backend.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mb-16">
        <Link
          href="#categories"
          className="inline-flex items-center justify-center px-8 py-3.5 rounded-lg text-base font-semibold text-white bg-slate-900 hover:bg-slate-800 shadow-md transition-all"
        >
          Book Your Mock Interview — ₹199
        </Link>
        <Link
          href="#how-it-works"
          className="inline-flex items-center justify-center px-8 py-3.5 rounded-lg text-base font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 transition-all"
        >
          Explore How It Works
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full text-left">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-sky-50 flex items-center justify-center text-sky-600 mb-4">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Real Human Expert</h3>
          <p className="text-sm text-slate-600">No robotic scripts or simulated bots. Experienced practitioner evaluating real engineering trade-offs.</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600 mb-4">
            <Clock className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Same-Day Contact</h3>
          <p className="text-sm text-slate-600">Personal coordinator outreach on the same day of payment to arrange your interview slot.</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600 mb-4">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Transparent ₹199 Fee</h3>
          <p className="text-sm text-slate-600">Single clear 45–60 minute package. No hidden charges or unexpected upsells.</p>
        </div>
      </div>
    </main>
  );
}
