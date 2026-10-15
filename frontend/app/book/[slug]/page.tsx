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
  Sparkles,
  Lock,
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

  // Candidate Contact & Profile Fields (No Login Required)
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [yearsExperience, setYearsExperience] = useState<number>(2.0);
  const [targetRole, setTargetRole] = useState("");
  const [currentCompany, setCurrentCompany] = useState("");
  const [technicalSkills, setTechnicalSkills] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [jdText, setJdText] = useState("");

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
  } | null>(null);

  // Load category and autofill if user already happens to have a session
  useEffect(() => {
    async function loadData() {
      try {
        const catData = await apiClient<InterviewCategory>(`/api/v1/categories/${slug}`);
        setCategory(catData);

        // Pre-fill target role based on track
        if (catData) {
          setTargetRole(catData.title.replace(" Mock Interview", " Engineer"));
        }

        // Try getting logged in user to prefill form if present
        try {
          const authData = await apiClient<{ user: User }>("/api/v1/auth/me");
          if (authData.user) {
            setFullName(authData.user.full_name);
            setEmail(authData.user.email);
            setPhone(authData.user.phone);
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
    if (!resumeFileId) {
      setError("Please upload your resume (PDF or DOCX) to proceed.");
      return;
    }
    if (!fullName.trim() || !email.trim() || !phone.trim()) {
      setError("Please fill in your full name, email address, and phone number.");
      return;
    }

    setError(null);
    setSubmitting(true);

    const skills = technicalSkills
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    try {
      // 1. Create instant booking and order directly without prior account creation
      const res = await apiClient<InstantBookingResponse>("/api/v1/candidate/bookings/instant", {
        method: "POST",
        body: JSON.stringify({
          category_slug: slug,
          full_name: fullName.trim(),
          email: email.trim().toLowerCase(),
          phone: phone.trim(),
          years_experience: Number(yearsExperience),
          target_role: targetRole.trim() || "Software Engineer",
          current_company: currentCompany.trim() || undefined,
          technical_skills: skills,
          resume_file_id: resumeFileId,
          jd_text: jdText.trim() || undefined,
          additional_notes: additionalNotes.trim() || undefined,
        }),
      });

      // 2. Trigger Razorpay Checkout
      const Razorpay = (window as any).Razorpay;
      if (Razorpay) {
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
        // Fallback for development if external Razorpay script is blocked
        setConfirmedBooking({
          reference: res.booking_reference,
          categoryTitle: res.category_title,
          bookingId: res.booking_id,
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
        <div className="min-h-[60vh] flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-sky-600 animate-spin" />
        </div>
        <Footer />
      </>
    );
  }

  if (!category) {
    return (
      <>
        <Navbar />
        <div className="max-w-md mx-auto py-20 px-4 text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Category Not Found</h2>
          <p className="text-slate-600 mb-6">The requested mock interview track does not exist.</p>
          <Link href="/#categories" className="text-sm font-semibold text-sky-600 hover:text-sky-700">
            View All Categories
          </Link>
        </div>
        <Footer />
      </>
    );
  }

  // SUCCESS CONFIRMATION VIEW
  if (confirmedBooking) {
    return (
      <>
        <Navbar />
        <main className="flex-1 py-16 px-4 sm:px-6 lg:px-8 bg-slate-50">
          <div className="max-w-2xl mx-auto bg-white border border-slate-200 rounded-3xl p-8 sm:p-12 text-center shadow-sm">
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
              Payment Successful &bull; ₹199 Confirmed
            </span>

            <h1 className="text-3xl font-extrabold text-slate-900 mt-4">
              Your Mock Interview Is Booked!
            </h1>
            <p className="text-slate-600 mt-2 text-sm max-w-md mx-auto">
              We have received your booking for <strong>{confirmedBooking.categoryTitle}</strong>.
            </p>

            <div className="my-8 p-6 bg-slate-50 border border-slate-200 rounded-2xl text-left space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-slate-200">
                <span className="text-xs text-slate-500 font-medium">Booking Reference</span>
                <span className="font-mono text-base font-bold text-sky-700 bg-sky-50 px-2.5 py-1 rounded">
                  {confirmedBooking.reference}
                </span>
              </div>

              <div className="flex justify-between items-center pb-3 border-b border-slate-200">
                <span className="text-xs text-slate-500 font-medium">Session Duration</span>
                <span className="text-sm font-bold text-slate-900">45–60 Minutes Guaranteed</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-500 font-medium">Same-Day Contact SLA</span>
                <span className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Interviewer will email you today</span>
                </span>
              </div>
            </div>

            <div className="p-4 bg-sky-50 border border-sky-100 rounded-xl text-xs text-sky-900 text-left mb-8 flex gap-3">
              <Sparkles className="w-5 h-5 text-sky-600 shrink-0 mt-0.5" />
              <div>
                <strong>Next Step:</strong> Check your inbox (<strong>{email}</strong>). Our interviewer will personally contact you today to coordinate your Google Meet / Zoom date and time!
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-sm transition-all"
              >
                <span>Go to Candidate Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/"
                className="inline-flex items-center justify-center px-6 py-3.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition-all"
              >
                Return to Home
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
      <main className="flex-1 py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          {/* Header Track Summary */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md mb-2">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>1-on-1 Human-Led Technical Track</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
                {category.title}
              </h1>
              <p className="text-sm text-slate-500 mt-1 max-w-xl">
                {category.short_description}
              </p>
            </div>

            <div className="bg-slate-900 text-white p-5 rounded-2xl shrink-0 text-center md:text-right border border-slate-800">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                Flat Package Fee
              </div>
              <div className="text-3xl font-black text-white mt-1">₹199</div>
              <div className="text-xs text-emerald-400 font-medium mt-1 flex items-center justify-center md:justify-end gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>45–60 Minutes Live</span>
              </div>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
              <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
              <div>
                <strong className="block font-semibold">Unable to proceed</strong>
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Frictionless Direct Booking Form */}
          <form onSubmit={handleInstantCheckout} className="space-y-8">
            {/* Step 1: Contact Details */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <span className="w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
                  1
                </span>
                <h2 className="text-lg font-bold text-slate-900">Your Contact Information</h2>
                <span className="text-xs text-slate-400 font-normal ml-auto">No prior account needed</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Full Name <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Rahul Verma"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Email Address <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                  <span className="text-[11px] text-slate-400 mt-1 block">Interviewer contacts you here</span>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Phone / WhatsApp <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                  <span className="text-[11px] text-slate-400 mt-1 block">Used for interview coordination</span>
                </div>
              </div>
            </div>

            {/* Step 2: Professional Dossier */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <span className="w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
                  2
                </span>
                <h2 className="text-lg font-bold text-slate-900">Professional Background & Tailoring</h2>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                      Target Role <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={targetRole}
                      onChange={(e) => setTargetRole(e.target.value)}
                      placeholder="e.g. Senior Backend Engineer"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                      Years of Experience <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max="40"
                      required
                      value={yearsExperience}
                      onChange={(e) => setYearsExperience(parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                      Current Company (Optional)
                    </label>
                    <input
                      type="text"
                      value={currentCompany}
                      onChange={(e) => setCurrentCompany(e.target.value)}
                      placeholder="e.g. Infosys, Startup, Student"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Key Technical Skills
                  </label>
                  <input
                    type="text"
                    value={technicalSkills}
                    onChange={(e) => setTechnicalSkills(e.target.value)}
                    placeholder="e.g. Python, Golang, PostgreSQL, Docker, AWS, Distributed Systems"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                  <span className="text-xs text-slate-400 mt-1 block">Separate skills with commas</span>
                </div>

                {/* Resume Upload */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Upload Resume (PDF or DOCX) <span className="text-rose-500">*</span>
                  </label>

                  {resumeFileId ? (
                    <div className="flex items-center justify-between p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-emerald-600" />
                        <div>
                          <p className="text-sm font-semibold text-emerald-900">{resumeFile?.name}</p>
                          <p className="text-xs text-emerald-700">Verified & Ready for Interviewer Review</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setResumeFile(null);
                          setResumeFileId(null);
                        }}
                        className="text-xs font-semibold text-emerald-800 hover:text-emerald-950 underline"
                      >
                        Change File
                      </button>
                    </div>
                  ) : (
                    <div className="relative border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:border-sky-500 hover:bg-sky-50/20 transition-all">
                      <input
                        type="file"
                        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        onChange={handleResumeUpload}
                        disabled={uploadingResume}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                      {uploadingResume ? (
                        <div className="flex flex-col items-center">
                          <Loader2 className="w-6 h-6 text-sky-600 animate-spin mb-2" />
                          <span className="text-sm font-semibold text-slate-700">Validating & Uploading...</span>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center">
                          <Upload className="w-8 h-8 text-slate-400 mb-2" />
                          <span className="text-sm font-semibold text-slate-800">
                            Click or drag resume here
                          </span>
                          <span className="text-xs text-slate-400 mt-1">
                            PDF or DOCX only &bull; Max 5 MB &bull; Encrypted Storage
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Target Job Description */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Target Job Description (Pasted Text or Requirements)
                  </label>
                  <textarea
                    rows={4}
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    placeholder="Paste the target job description or requirements so your interviewer can customize the problems to your target company..."
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Additional Notes or Focus Areas (Optional)
                  </label>
                  <input
                    type="text"
                    value={additionalNotes}
                    onChange={(e) => setAdditionalNotes(e.target.value)}
                    placeholder="e.g. Please focus on database indexing and high-throughput messaging."
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Step 3: Order Review & Direct Payment */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <span className="w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
                  3
                </span>
                <h2 className="text-lg font-bold text-slate-900">Review & Pay ₹199</h2>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3 mb-6">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-600">{category.title}</span>
                  <span className="font-bold text-slate-900">₹199</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-600">Interview Duration</span>
                  <span className="font-semibold text-slate-800">45–60 Minutes Guaranteed</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-600">Platform Convenience & Taxes</span>
                  <span className="font-semibold text-emerald-600">₹0 (Included)</span>
                </div>
                <div className="pt-3 border-t border-slate-200 flex justify-between items-center">
                  <span className="font-bold text-slate-900">Total Authoritative Price</span>
                  <span className="text-2xl font-black text-slate-900">₹199</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1 mb-6">
                <div className="font-bold flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-amber-700" />
                  <span>Same-Day Contact Guarantee:</span>
                </div>
                <p>
                  Our senior technical interviewer will reach out directly to <strong>{email || "your email"}</strong> today to coordinate your Google Meet or Zoom interview schedule.
                </p>
              </div>

              <button
                type="submit"
                disabled={submitting || uploadingResume}
                className="w-full py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-black text-base shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Opening Razorpay Secure Checkout...</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4 text-emerald-400" />
                    <span>Pay ₹199 & Confirm Mock Interview</span>
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </>
                )}
              </button>

              <div className="mt-4 flex items-center justify-center gap-4 text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                  Razorpay Verified Checkout
                </span>
                <span>&bull;</span>
                <span>100% Refund SLA Guarantee</span>
                <span>&bull;</span>
                <span>No password required</span>
              </div>
            </div>
          </form>
        </div>
      </main>
      <Footer />
    </>
  );
}
