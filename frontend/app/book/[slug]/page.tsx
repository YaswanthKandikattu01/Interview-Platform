"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { apiClient } from "@/services/api";
import { InterviewCategory } from "@/types/category";
import { User, CandidateProfile } from "@/types/auth";
import { BookingDetailResponse, FileUploadResponse } from "@/types/booking";
import {
  Clock,
  ShieldCheck,
  CheckCircle2,
  Upload,
  FileText,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Loader2,
  CalendarX2,
} from "lucide-react";

export default function BookInterviewPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const [category, setCategory] = useState<InterviewCategory | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [candidateProfile, setCandidateProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Form Fields
  const [yearsExperience, setYearsExperience] = useState<number>(2.0);
  const [targetRole, setTargetRole] = useState("");
  const [currentCompany, setCurrentCompany] = useState("");
  const [technicalSkills, setTechnicalSkills] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [jdText, setJdText] = useState("");

  // Uploaded File States
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeFileId, setResumeFileId] = useState<string | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdFileId, setJdFileId] = useState<string | null>(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadingJd, setUploadingJd] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Load category and auth profile
  useEffect(() => {
    async function loadData() {
      try {
        const catData = await apiClient<InterviewCategory>(`/api/v1/categories/${slug}`);
        setCategory(catData);

        // Try getting logged in user
        const authData = await apiClient<{ user: User; profile: CandidateProfile | null }>("/api/v1/auth/me");
        setCurrentUser(authData.user);
        if (authData.profile) {
          setCandidateProfile(authData.profile);
          setYearsExperience(authData.profile.years_experience);
          setTargetRole(authData.profile.target_role);
          setCurrentCompany(authData.profile.current_company || "");
          setTechnicalSkills(authData.profile.technical_skills?.join(", ") || "");
        }
      } catch (err: any) {
        // User not logged in or invalid category
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [slug]);

  // Handle Resume File Upload
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
      setError(err.message || "Failed to upload resume.");
      setResumeFile(null);
    } finally {
      setUploadingResume(false);
    }
  };

  // Handle JD File Upload
  const handleJdUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError("Job description file must be under 5 MB.");
      return;
    }

    setJdFile(file);
    setUploadingJd(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("file_purpose", "JOB_DESCRIPTION");

    try {
      const res = await apiClient<FileUploadResponse>("/api/v1/candidate/upload", {
        method: "POST",
        body: formData,
      });
      setJdFileId(res.file_id);
    } catch (err: any) {
      setError(err.message || "Failed to upload job description.");
      setJdFile(null);
    } finally {
      setUploadingJd(false);
    }
  };

  // Submit Booking Draft
  const handleCreateDraft = async () => {
    if (!resumeFileId) {
      setError("Please upload your resume (PDF or DOCX) to proceed.");
      return;
    }

    setError(null);
    setSubmitting(true);

    const skills = technicalSkills
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    try {
      const draft = await apiClient<BookingDetailResponse>("/api/v1/candidate/bookings/draft", {
        method: "POST",
        body: JSON.stringify({
          category_slug: slug,
          resume_file_id: resumeFileId,
          jd_file_id: jdFileId || undefined,
          jd_text: jdText.trim() || undefined,
          additional_notes: additionalNotes.trim() || undefined,
          years_experience: Number(yearsExperience),
          target_role: targetRole || "Software Engineer",
          current_company: currentCompany || undefined,
          technical_skills: skills,
        }),
      });

      // Redirect to candidate dashboard or checkout
      router.push(`/dashboard?new_booking=${draft.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create booking draft.");
    } finally {
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

  if (!currentUser) {
    return (
      <>
        <Navbar />
        <div className="max-w-md mx-auto py-20 px-4 text-center">
          <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mx-auto mb-4">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 mb-2">Account Required</h2>
          <p className="text-sm text-slate-600 mb-6">
            Please log in or create a candidate account before booking your ₹199 mock interview for <strong>{category.title}</strong>.
          </p>
          <div className="flex flex-col gap-3">
            <Link
              href="/register"
              className="py-3 px-4 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm"
            >
              Create Candidate Account
            </Link>
            <Link
              href="/login"
              className="py-3 px-4 rounded-xl text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50"
            >
              Sign In to Existing Account
            </Link>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="flex-1 py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-3xl mx-auto">
          {/* Header Summary Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm mb-8">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-6 mb-6">
              <div>
                <span className="text-xs font-bold text-sky-600 uppercase tracking-wider block mb-1">
                  1-on-1 Mock Interview
                </span>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  {category.title}
                </h1>
              </div>
              <div className="sm:text-right">
                <span className="text-3xl font-black text-slate-900">₹199</span>
                <span className="block text-xs text-slate-500 font-medium">45–60 Minutes Session</span>
              </div>
            </div>

            {/* Step Progress Bar */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs font-semibold">
              <div
                className={`py-2 rounded-lg ${
                  step === 1 ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600"
                }`}
              >
                1. Professional Details
              </div>
              <div
                className={`py-2 rounded-lg ${
                  step === 2 ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600"
                }`}
              >
                2. Resume & JD Upload
              </div>
              <div
                className={`py-2 rounded-lg ${
                  step === 3 ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600"
                }`}
              >
                3. Review Order (₹199)
              </div>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-4 mb-6 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* STEP 1: Professional Details */}
          {step === 1 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-5">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Your Professional Context</h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    Target Job Role *
                  </label>
                  <input
                    type="text"
                    required
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    placeholder="e.g. SDE-2 Backend, Lead Architect"
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    Years of Experience *
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="40"
                    required
                    value={yearsExperience}
                    onChange={(e) => setYearsExperience(Number(e.target.value))}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Current or Previous Company (Optional)
                </label>
                <input
                  type="text"
                  value={currentCompany}
                  onChange={(e) => setCurrentCompany(e.target.value)}
                  placeholder="e.g. Microsoft, Flipkart, Startup"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Core Technical Skills
                </label>
                <input
                  type="text"
                  value={technicalSkills}
                  onChange={(e) => setTechnicalSkills(e.target.value)}
                  placeholder="e.g. Python, Distributed Systems, Redis, Docker"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="button"
                  onClick={() => {
                    if (!targetRole.trim()) {
                      setError("Please specify your target job role.");
                      return;
                    }
                    setError(null);
                    setStep(2);
                  }}
                  className="inline-flex items-center gap-2 py-3 px-6 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm"
                >
                  <span>Next: Upload Documents</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Resume & JD Upload */}
          {step === 2 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-1">Resume & Job Description</h3>
                <p className="text-xs text-slate-500">
                  Only PDF and DOCX formats allowed. Maximum 5 MB per file.
                </p>
              </div>

              {/* Resume Upload */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Resume (PDF / DOCX) *
                </label>
                <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 text-center hover:border-slate-400 transition-colors">
                  <input
                    type="file"
                    id="resume-upload"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleResumeUpload}
                    className="hidden"
                  />
                  <label htmlFor="resume-upload" className="cursor-pointer flex flex-col items-center">
                    <Upload className="w-8 h-8 text-slate-400 mb-2" />
                    <span className="text-sm font-bold text-slate-800">
                      {resumeFile ? resumeFile.name : "Click to select your resume"}
                    </span>
                    <span className="text-xs text-slate-400 mt-1">PDF or DOCX up to 5 MB</span>
                  </label>
                </div>
                {uploadingResume && (
                  <div className="flex items-center gap-2 text-xs text-sky-600 mt-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Verifying file magic bytes and uploading...</span>
                  </div>
                )}
                {resumeFileId && (
                  <div className="flex items-center gap-2 text-xs text-emerald-600 font-semibold mt-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Resume securely verified and attached!</span>
                  </div>
                )}
              </div>

              {/* JD Input */}
              <div className="space-y-3 pt-2">
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Target Job Description (Optional)
                </label>
                <textarea
                  rows={4}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the target job description or requirements here..."
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                />

                <div className="text-xs text-slate-500 text-center">or upload JD as file</div>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleJdUpload}
                  className="text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
                />
                {jdFileId && (
                  <div className="text-xs text-emerald-600 font-medium">JD file attached.</div>
                )}
              </div>

              <div className="pt-4 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="inline-flex items-center gap-1.5 py-2.5 px-4 rounded-xl text-sm font-semibold text-slate-600 hover:text-slate-900"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>
                <button
                  type="button"
                  disabled={!resumeFileId}
                  onClick={() => {
                    if (!resumeFileId) {
                      setError("Please upload and verify your resume.");
                      return;
                    }
                    setError(null);
                    setStep(3);
                  }}
                  className="inline-flex items-center gap-2 py-3 px-6 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 disabled:opacity-50 shadow-sm"
                >
                  <span>Review Order</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Order Review & Cutoff Policy */}
          {step === 3 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-slate-900">Review & Confirm Your Order</h3>

              {/* Order breakdown */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-3 text-sm">
                <div className="flex justify-between items-center text-slate-600">
                  <span>Track</span>
                  <span className="font-bold text-slate-900">{category.title}</span>
                </div>
                <div className="flex justify-between items-center text-slate-600">
                  <span>Session Length</span>
                  <span className="font-bold text-slate-900">45–60 minutes</span>
                </div>
                <div className="flex justify-between items-center text-slate-600">
                  <span>Target Role</span>
                  <span className="font-bold text-slate-900">{targetRole}</span>
                </div>
                <div className="flex justify-between items-center text-slate-600">
                  <span>Resume Attached</span>
                  <span className="font-bold text-emerald-600">Verified ({resumeFile?.name})</span>
                </div>
                <div className="pt-3 border-t border-slate-200 flex justify-between items-center text-base">
                  <span className="font-bold text-slate-900">Total Due Today</span>
                  <span className="font-black text-2xl text-slate-900">₹199</span>
                </div>
              </div>

              {/* Crucial Scheduling Guarantee & Cutoff Policy Notice */}
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-2">
                <div className="flex items-center gap-2 font-bold">
                  <Clock className="w-4 h-4 text-amber-700" />
                  <span>Same-Day Contact Commitment (Asia/Kolkata)</span>
                </div>
                <p className="leading-relaxed">
                  Our human interviewer personally contacts you via email to schedule your session.
                  Bookings made before <strong>08:00 PM IST</strong> receive personal outreach by <strong>11:59 PM IST today</strong>.
                  Bookings made after 08:00 PM IST will be contacted by 12:00 PM IST tomorrow morning.
                </p>
                <div className="flex items-center gap-1.5 text-amber-800 font-medium pt-1">
                  <CalendarX2 className="w-3.5 h-3.5" />
                  <span>No public slot booking or countdown timers. Your interviewer personally arranges the slot.</span>
                </div>
              </div>

              <div className="pt-4 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="inline-flex items-center gap-1.5 py-2.5 px-4 rounded-xl text-sm font-semibold text-slate-600 hover:text-slate-900"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>
                <button
                  type="button"
                  disabled={submitting}
                  onClick={handleCreateDraft}
                  className="inline-flex items-center gap-2 py-3.5 px-8 rounded-xl text-base font-bold text-white bg-slate-900 hover:bg-slate-800 disabled:opacity-50 shadow-md transition-all"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Creating Booking...</span>
                    </>
                  ) : (
                    <>
                      <span>Proceed to Confirm Booking — ₹199</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
