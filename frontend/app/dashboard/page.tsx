"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { apiClient } from "@/services/api";
import { User, CandidateProfile } from "@/types/auth";
import { BookingDetailResponse } from "@/types/booking";
import {
  Clock,
  Video,
  CheckCircle2,
  Calendar,
  AlertCircle,
  Loader2,
  User as UserIcon,
  BookOpen,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const newBookingId = searchParams.get("new_booking");

  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [bookings, setBookings] = useState<BookingDetailResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"bookings" | "profile">("bookings");

  // Profile Edit State
  const [editExperience, setEditExperience] = useState(0);
  const [editTargetRole, setEditTargetRole] = useState("");
  const [editCompany, setEditCompany] = useState("");
  const [editSkills, setEditSkills] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const authData = await apiClient<{ user: User; profile: CandidateProfile | null }>("/api/v1/auth/me");
        setUser(authData.user);
        if (authData.profile) {
          setProfile(authData.profile);
          setEditExperience(authData.profile.years_experience);
          setEditTargetRole(authData.profile.target_role);
          setEditCompany(authData.profile.current_company || "");
          setEditSkills(authData.profile.technical_skills?.join(", ") || "");
        }

        const myBookings = await apiClient<BookingDetailResponse[]>("/api/v1/candidate/bookings");
        setBookings(myBookings);
      } catch (err: any) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [router]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileSuccess(null);

    const skills = editSkills
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    try {
      const updated = await apiClient<CandidateProfile>("/api/v1/candidate/profile", {
        method: "PUT",
        body: JSON.stringify({
          years_experience: Number(editExperience),
          target_role: editTargetRole,
          current_company: editCompany || undefined,
          technical_skills: skills,
        }),
      });
      setProfile(updated);
      setProfileSuccess("Profile updated successfully!");
    } catch (err: any) {
      // Error handling
    } finally {
      setSavingProfile(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-sky-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Top Banner / Welcome */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-sky-600 uppercase tracking-wider block mb-1">
            Candidate Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Welcome back, {user?.full_name}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {user?.email} • {profile?.target_role || "Software Engineer"}
          </p>
        </div>

        <Link
          href="/#categories"
          className="inline-flex items-center gap-2 py-3 px-5 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm transition-all"
        >
          <span>Book Another Interview (₹199)</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {newBookingId && (
        <div className="mb-8 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <span className="font-bold text-sm">Booking Draft Created!</span>
              <p className="text-xs text-amber-800">
                Proceed with payment to lock in your ₹199 session and trigger same-day interviewer outreach.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-slate-200 mb-8">
        <button
          onClick={() => setActiveTab("bookings")}
          className={`flex items-center gap-2 pb-3 px-4 font-semibold text-sm border-b-2 transition-all ${
            activeTab === "bookings"
              ? "border-slate-900 text-slate-900"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>My Mock Interviews ({bookings.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("profile")}
          className={`flex items-center gap-2 pb-3 px-4 font-semibold text-sm border-b-2 transition-all ${
            activeTab === "profile"
              ? "border-slate-900 text-slate-900"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <UserIcon className="w-4 h-4" />
          <span>Professional Profile</span>
        </button>
      </div>

      {/* TAB 1: BOOKINGS LIST */}
      {activeTab === "bookings" && (
        <div className="space-y-6">
          {bookings.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
              <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-slate-900 mb-2">No Mock Interviews Booked Yet</h3>
              <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
                Practice 1-on-1 technical interviews with a senior engineer in System Design, DSA, AI, Full Stack, Frontend, or Backend.
              </p>
              <Link
                href="/#categories"
                className="inline-flex items-center gap-2 py-3 px-6 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm"
              >
                <span>Explore Tracks & Book — ₹199</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            bookings.map((booking) => (
              <div
                key={booking.id}
                className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm hover:border-slate-300 transition-all"
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4 mb-5">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
                        {booking.booking_reference}
                      </span>
                      <span className="text-xs font-semibold text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded-md">
                        {booking.duration_display}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">{booking.category_title}</h3>
                  </div>

                  <div className="sm:text-right">
                    <span className="text-2xl font-black text-slate-900">₹199</span>
                    <span className="block text-xs text-slate-500">Paid Amount</span>
                  </div>
                </div>

                {/* Status-Aware Timeline Box */}
                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 mb-5">
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-sky-600 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-bold text-slate-900">{booking.status_headline}</h4>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        {booking.status_message}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Meeting Link (if scheduled) */}
                {booking.meeting_url && (
                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
                    <div className="flex items-center gap-2 text-emerald-900">
                      <Video className="w-5 h-5 text-emerald-600 shrink-0" />
                      <div>
                        <span className="text-xs font-bold block">Interview Confirmed:</span>
                        <span className="text-xs text-emerald-700">
                          {booking.scheduled_start
                            ? new Date(booking.scheduled_start).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })
                            : "Scheduled"}
                        </span>
                      </div>
                    </div>
                    <a
                      href={booking.meeting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 py-2 px-4 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs"
                    >
                      <span>Join Meeting Link</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                )}

                <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400 pt-2 border-t border-slate-100">
                  <span>Target Role: {booking.target_role} ({booking.years_experience} yrs exp)</span>
                  <span>Booked: {new Date(booking.created_at).toLocaleDateString("en-IN")}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 2: PROFILE EDITOR */}
      {activeTab === "profile" && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm max-w-2xl">
          <h3 className="text-lg font-bold text-slate-900 mb-2">Professional Profile</h3>
          <p className="text-xs text-slate-500 mb-6">
            This information is shared with your human interviewer so they can calibrate technical questions to your seniority.
          </p>

          {profileSuccess && (
            <div className="flex items-center gap-2 p-3.5 mb-6 text-sm text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-xl">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{profileSuccess}</span>
            </div>
          )}

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Target Role
              </label>
              <input
                type="text"
                required
                value={editTargetRole}
                onChange={(e) => setEditTargetRole(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Years of Experience
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="40"
                  required
                  value={editExperience}
                  onChange={(e) => setEditExperience(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Current Company
                </label>
                <input
                  type="text"
                  value={editCompany}
                  onChange={(e) => setEditCompany(e.target.value)}
                  placeholder="e.g. Swiggy, Amazon"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Technical Skills (comma-separated)
              </label>
              <input
                type="text"
                value={editSkills}
                onChange={(e) => setEditSkills(e.target.value)}
                placeholder="Python, React, System Design, PostgreSQL"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
              />
            </div>

            <div className="pt-4 flex justify-end">
              <button
                type="submit"
                disabled={savingProfile}
                className="py-2.5 px-6 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 disabled:opacity-50 shadow-sm"
              >
                {savingProfile ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default function CandidateDashboardPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 bg-slate-50">
        <Suspense fallback={<div>Loading dashboard...</div>}>
          <DashboardContent />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}
