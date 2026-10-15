"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { apiClient } from "@/services/api";
import { CheckCircle2, AlertCircle, Loader2, ArrowRight } from "lucide-react";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setError("No email verification token provided in the URL.");
      setLoading(false);
      return;
    }

    apiClient<{ is_email_verified: boolean }>("/api/v1/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
      .then(() => {
        setSuccess(true);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Email verification failed or token expired.");
        setLoading(false);
      });
  }, [token]);

  return (
    <div className="max-w-md w-full bg-white border border-slate-200 rounded-2xl p-8 text-center shadow-sm">
      {loading && (
        <div className="py-8 space-y-4">
          <Loader2 className="w-10 h-10 text-sky-600 animate-spin mx-auto" />
          <h2 className="text-xl font-bold text-slate-900">Verifying your email...</h2>
          <p className="text-sm text-slate-500">Please wait a moment while we activate your candidate account.</p>
        </div>
      )}

      {!loading && success && (
        <div className="py-6 space-y-4">
          <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900">Email Verified!</h2>
          <p className="text-sm text-slate-600">
            Your candidate email address has been verified. You can now log in and complete your mock interview booking.
          </p>
          <div className="pt-4">
            <Link
              href="/login"
              className="w-full inline-flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm"
            >
              <span>Continue to Login</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="py-6 space-y-4">
          <div className="w-14 h-14 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900">Verification Failed</h2>
          <p className="text-sm text-red-600">{error}</p>
          <div className="pt-4 flex flex-col gap-2">
            <Link
              href="/login"
              className="text-sm font-semibold text-slate-700 hover:text-slate-900 py-2"
            >
              Back to Login
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 flex items-center justify-center py-16 px-4 bg-slate-50">
        <Suspense fallback={<div>Loading verification...</div>}>
          <VerifyEmailContent />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}
