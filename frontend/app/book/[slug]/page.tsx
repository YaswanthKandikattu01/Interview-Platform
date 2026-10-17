"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Script from "next/script";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { apiClient } from "@/services/api";
import { InterviewCategory } from "@/types/category";
import { User } from "@/types/auth";
import { FileUploadResponse } from "@/types/booking";
import {
  Clock,
  ShieldCheck,
  CheckCircle2,
  Upload,
  FileText,
  AlertCircle,
  ArrowRight,
  Loader2,
  Lock,
  MessageSquare,
} from "lucide-react";

interface InstantBookingResponse {
  booking_id: string;
  booking_reference: string;
  order_id: string;
  amount_paise: number;
  currency: string;
  key_id: string;
  access_token: string;
  candidate_name: string;
  candidate_email: string;
  category_title: string;
  duration_display: string;
}

export default function BookInterviewPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const [category, setCategory] = useState<InterviewCategory | null>(null);
  const [loading, setLoading] = useState(true);

  // Simplified Candidate Fields
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [comments, setComments] = useState("");

  // Upload States
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeFileId, setResumeFileId] = useState<string | null>(null);
  const [uploadingResume, setUploadingResume] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Success Confirmation State
  const [confirmedBooking, setConfirmedBooking] = useState<{
    reference: string;
    categoryTitle: string;
    bookingId: string;
    priceInr: number;
  } | null>(null);

  // Dynamic Price & Duration from Category
  const priceInr = category?.active_price ? category.active_price.amount_paise / 100 : 199;
  const durationDisplay = category?.active_price ? category.active_price.duration_display : "45–60 minutes";

  // Load category and autofill if user already happens to have a session
  useEffect(() => {
    async function loadData() {
      try {
        const catData = await apiClient<InterviewCategory>(`/api/v1/categories/${slug}`);
        setCategory(catData);

        // Try getting logged in user to prefill form if present
        try {
          const authData = await apiClient<{ user: User }>("/api/v1/auth/me");
          if (authData.user) {
            setFullName(authData.user.full_name);
            setEmail(authData.user.email);
            if (authData.user.phone) setPhone(authData.user.phone);
          }
        } catch {
          // Guest user - perfectly fine!
        }
      } catch (err: any) {
        console.error("Failed to load category", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [slug]);

  // Handle Resume Upload (Guest supported)
  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError("Resume file must be under 5 MB.");
      return;
    }

    setResumeFile(file);
    setUploadingResume(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("file_purpose", "RESUME");

    try {
      const res = await apiClient<FileUploadResponse>("/api/v1/candidate/upload", {
        method: "POST",
        body: formData,
      });
      setResumeFileId(res.file_id);
    } catch (err: any) {
      setError(err.message || "Failed to upload resume. Ensure file is a valid PDF or DOCX.");
      setResumeFile(null);
    } finally {
      setUploadingResume(false);
    }
  };

  // Instant Checkout: One-Click Booking & Razorpay Payment
  const handleInstantCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim()) {
      setError("Please fill in your full name and email address.");
      return;
    }
    if (!resumeFileId) {
      setError("Please upload your resume (PDF or DOCX) to proceed.");
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      // 1. Create instant booking and order directly without prior account creation
      const res = await apiClient<InstantBookingResponse>("/api/v1/candidate/bookings/instant", {
        method: "POST",
        body: JSON.stringify({
          category_slug: slug,
          full_name: fullName.trim(),
          email: email.trim().toLowerCase(),
          phone: phone.trim() || undefined,
          resume_file_id: resumeFileId,
          comments: comments.trim() || undefined,
          target_role: category?.title || "Engineering Candidate",
        }),
      });

      // 2. Trigger Razorpay Checkout (or Simulated Checkout in mock mode)
      const isMockMode = res.key_id?.startsWith("rzp_test_mock");
      const Razorpay = (window as any).Razorpay;

      if (Razorpay && !isMockMode) {
        const options = {
          key: res.key_id,
          amount: res.amount_paise,
          currency: res.currency,
          name: "MockInterview.in",
          description: `${res.category_title} (${res.duration_display})`,
          order_id: res.order_id,
          prefill: {
            name: fullName,
            email: email,
            contact: phone,
          },
          theme: {
            color: "#0f172a",
          },
          handler: async function (paymentResponse: any) {
            try {
              // 3. Verify Payment Signature
              await apiClient("/api/v1/payments/verify", {
                method: "POST",
                body: JSON.stringify({
                  booking_id: res.booking_id,
                  razorpay_order_id: paymentResponse.razorpay_order_id,
                  razorpay_payment_id: paymentResponse.razorpay_payment_id,
                  razorpay_signature: paymentResponse.razorpay_signature,
                }),
              });

              setConfirmedBooking({
                reference: res.booking_reference,
                categoryTitle: res.category_title,
                bookingId: res.booking_id,
                priceInr: res.amount_paise / 100,
              });
            } catch (vErr: any) {
              setError("Payment verification encountered an issue. Please contact support with payment ID: " + paymentResponse.razorpay_payment_id);
            }
          },
          modal: {
            ondismiss: function () {
              setSubmitting(false);
            },
          },
        };

        const rzp = new Razorpay(options);
        rzp.open();
      } else {
        // Automatic Simulated Payment verification for development/testing
        try {
          const fakePaymentId = "pay_sim_" + Math.random().toString(36).substring(2, 12);
          await apiClient("/api/v1/payments/verify", {
            method: "POST",
            body: JSON.stringify({
              booking_id: res.booking_id,
              razorpay_order_id: res.order_id,
              razorpay_payment_id: fakePaymentId,
              razorpay_signature: "mock_signature_valid",
            }),
          });
        } catch (simErr: any) {
          console.warn("Simulated payment verification note:", simErr);
        }

        setConfirmedBooking({
          reference: res.booking_reference,
          categoryTitle: res.category_title,
          bookingId: res.booking_id,
          priceInr: res.amount_paise / 100,
        });
      }
    } catch (err: any) {
      setError(err.message || "Failed to process booking. Please try again.");
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="min-h-[60vh] flex items-center justify-center bg-slate-50 dark:bg-slate-950">
          <Loader2 className="w-8 h-8 text-sky-600 dark:text-sky-400 animate-spin" />
        </div>
        <Footer />
      </>
    );
  }

  if (!category) {
    return (
      <>
        <Navbar />
        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6 bg-slate-50 dark:bg-slate-950">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Category Not Found</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">The requested program does not exist.</p>
          <Link
            href="/"
            className="px-6 py-2.5 rounded-xl bg-slate-900 dark:bg-sky-600 text-white font-semibold text-sm hover:bg-slate-800 dark:hover:bg-sky-500"
          >
            Return to Programs
          </Link>
        </div>
        <Footer />
      </>
    );
  }

  // Confirmation Screen
  if (confirmedBooking) {
    return (
      <>
        <Navbar />
        <main className="flex-1 py-16 px-4 sm:px-6 lg:px-8 bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
          <div className="max-w-xl w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 sm:p-12 shadow-xl text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest block mb-2">
              Payment Confirmed
            </span>
            <h1 className="text-3xl font-black text-slate-900 dark:text-white mb-2">
              Your Booking Is Secured!
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
              We received your payment of <strong className="text-slate-900 dark:text-white">₹{confirmedBooking.priceInr}</strong> for the{" "}
              <strong className="text-slate-900 dark:text-white">{confirmedBooking.categoryTitle}</strong>.
            </p>

            {/* Reference Card */}
            <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 rounded-2xl p-6 text-left mb-8 space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700 text-xs">
                <span className="text-slate-500 dark:text-slate-400 font-medium">Booking Reference</span>
                <span className="font-mono font-bold text-slate-900 dark:text-white text-sm">
                  {confirmedBooking.reference}
                </span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700 text-xs">
                <span className="text-slate-500 dark:text-slate-400 font-medium">Program Track</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{confirmedBooking.categoryTitle}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500 dark:text-slate-400 font-medium">Scheduling Outreach</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">Guaranteed Today (IST)</span>
              </div>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
              A booking confirmation has been sent to your email. Our interviewer will contact you personally by email today to coordinate a mutually convenient date and time.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                href="/"
                className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 text-white font-bold text-sm shadow-md transition-all"
              >
                <span>Return to Home</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/#categories"
                className="inline-flex items-center justify-center px-6 py-3.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold text-sm transition-all"
              >
                Book Another Program
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="lazyOnload" />
      <Navbar />
      <main className="flex-1 py-12 px-4 sm:px-6 lg:px-8 bg-slate-50 dark:bg-slate-950 transition-colors">
        <div className="max-w-3xl mx-auto">
          {/* Header Track Summary */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 transition-colors">
            <div>
              <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 px-2.5 py-1 rounded-md mb-2">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>1-on-1 Human-Led Technical Program</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
                {category.title}
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-xl">
                {category.short_description}
              </p>
            </div>

            <div className="bg-slate-900 dark:bg-slate-800/80 text-white p-5 rounded-2xl shrink-0 text-center md:text-right border border-slate-800 dark:border-slate-700">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                Package Fee
              </div>
              <div className="text-3xl font-black text-white mt-1">₹{priceInr}</div>
              <div className="text-xs text-emerald-400 font-medium mt-1 flex items-center justify-center md:justify-end gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>{durationDisplay}</span>
              </div>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 text-sm flex items-start gap-3">
              <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 dark:text-rose-400 mt-0.5" />
              <div>
                <strong className="block font-semibold">Unable to proceed</strong>
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Frictionless Direct Booking Form */}
          <form onSubmit={handleInstantCheckout} className="space-y-6">
            {/* Step 1: Contact Details */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm transition-colors">
              <div className="flex items-center gap-2 mb-6">
                <span className="w-7 h-7 rounded-full bg-slate-900 dark:bg-sky-600 text-white text-xs font-bold flex items-center justify-center">
                  1
                </span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Your Contact Information</h2>
                <span className="text-xs text-slate-400 ml-auto">No account needed</span>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2">
                      Full Name <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="e.g. Rahul Verma"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white dark:bg-slate-800/80 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2">
                      Email Address <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@example.com"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white dark:bg-slate-800/80 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
                    />
                    <span className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 block">Interviewer contacts you here</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2">
                    Contact Number / WhatsApp <span className="text-slate-400 font-normal lowercase">(optional)</span>
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210 (optional)"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white dark:bg-slate-800/80 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
                  />
                  <span className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 block">Optional: for urgent WhatsApp scheduling coordination</span>
                </div>
              </div>
            </div>

            {/* Step 2: Resume Upload (Required) */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm transition-colors">
              <div className="flex items-center gap-2 mb-6">
                <span className="w-7 h-7 rounded-full bg-slate-900 dark:bg-sky-600 text-white text-xs font-bold flex items-center justify-center">
                  2
                </span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Upload Your Resume</h2>
                <span className="text-xs text-rose-500 font-semibold ml-auto">Required</span>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2">
                  Resume File (PDF or DOCX, max 5 MB) <span className="text-rose-500">*</span>
                </label>
                <div className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-colors ${
                  resumeFileId
                    ? "border-emerald-400 dark:border-emerald-600 bg-emerald-50/40 dark:bg-emerald-950/20"
                    : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 bg-slate-50/50 dark:bg-slate-800/40"
                }`}>
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleResumeUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  {uploadingResume ? (
                    <div className="flex flex-col items-center">
                      <Loader2 className="w-8 h-8 text-sky-600 dark:text-sky-400 animate-spin mb-2" />
                      <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Validating & uploading file...</span>
                    </div>
                  ) : resumeFileId ? (
                    <div className="flex items-center justify-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div className="text-left">
                        <span className="block text-sm font-bold text-slate-900 dark:text-white">{resumeFile?.name}</span>
                        <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Uploaded successfully (Click to replace)
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center mb-2">
                        <Upload className="w-5 h-5" />
                      </div>
                      <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                        Drop your resume here, or <span className="text-sky-600 dark:text-sky-400">browse</span>
                      </span>
                      <span className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                        Accepts PDF or Word (.docx) documents up to 5 MB
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Step 3: Comments & Suggestions for Interviewer */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-sm transition-colors">
              <div className="flex items-center gap-2 mb-4">
                <span className="w-7 h-7 rounded-full bg-slate-900 dark:bg-sky-600 text-white text-xs font-bold flex items-center justify-center">
                  3
                </span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Comments & Suggestions for the Interviewer</h2>
                <span className="text-xs text-slate-400 ml-auto">Optional</span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
                Share any specific topics, target companies (e.g. Google, Amazon, startups), areas you want to focus on, or questions you have so the interviewer has a clear idea about you before the session.
              </p>

              <div>
                <textarea
                  rows={4}
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder="e.g., Preparing for Senior Frontend at a FinTech startup. Please focus heavily on Next.js App Router performance, state management trade-offs, and behavioral engineering questions..."
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white dark:bg-slate-800/80 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
                />
              </div>
            </div>

            {/* Order Review & Direct Payment Checkout */}
            <div className="bg-slate-900 dark:bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 text-white shadow-xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
                <div>
                  <h3 className="text-lg font-bold text-white">Order Summary</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{category.title} ({durationDisplay})</p>
                </div>
                <div className="text-right">
                  <span className="text-xs uppercase text-slate-400 font-semibold block">Total Due</span>
                  <span className="text-3xl font-black text-white">₹{priceInr}</span>
                </div>
              </div>

              <div className="space-y-3 mb-6 text-xs text-slate-300">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>100% human senior software engineer</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Same-day scheduling email outreach (Asia/Kolkata timezone)</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>100% full refund guarantee if interviewer fails to contact within SLA</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting || !resumeFileId}
                className="w-full py-4 rounded-xl font-extrabold text-base bg-emerald-500 hover:bg-emerald-400 active:scale-[0.99] text-slate-950 shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing Secure Checkout...</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4" />
                    <span>Proceed to Secure Checkout — ₹{priceInr}</span>
                  </>
                )}
              </button>

              <div className="flex items-center justify-center gap-4 mt-4 text-[11px] text-slate-400">
                <span>🔒 256-bit SSL Encrypted</span>
                <span>•</span>
                <span>UPI, Cards, Netbanking</span>
                <span>•</span>
                <span>Zero Hidden Charges</span>
              </div>
            </div>
          </form>
        </div>
      </main>
      <Footer />
    </>
  );
}
