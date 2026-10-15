"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/api";
import { User } from "@/types/auth";
import {
  Calendar,
  Clock,
  Search,
  CheckCircle2,
  AlertCircle,
  FileText,
  Video,
  UserCheck,
  RotateCcw,
  XCircle,
  ExternalLink,
  ShieldAlert,
  Download,
  Star,
  ChevronRight,
  TrendingUp,
} from "lucide-react";

interface AdminOverview {
  total_revenue_paise: number;
  total_revenue_inr: number;
  total_bookings: number;
  awaiting_contact_count: number;
  overdue_contact_count: number;
  scheduled_count: number;
  completed_count: number;
  cancelled_count: number;
  upcoming_interviews: Array<{
    schedule_id: string;
    booking_id: string;
    booking_reference: string;
    category_title: string;
    scheduled_start: string;
    scheduled_end: string;
    meeting_url: string;
    candidate_target_role: string;
  }>;
}

interface BookingItem {
  id: string;
  booking_reference: string;
  category_title: string;
  category_slug: string;
  candidate_name: string;
  candidate_email: string;
  candidate_phone: string;
  payment_status: string;
  amount_paise: number;
  scheduling_status: string;
  contact_status: string;
  contact_deadline_at: string | null;
  first_contacted_at: string | null;
  scheduled_start: string | null;
  scheduled_end: string | null;
  meeting_url: string | null;
  created_at: string;
}

interface BookingDetail {
  id: string;
  booking_reference: string;
  category: { title: string; slug: string };
  candidate: { id: string; full_name: string; email: string; phone: string };
  professional_input: {
    years_experience: number;
    current_company: string | null;
    target_role: string | null;
    technical_skills: string[];
    resume_file_id: string | null;
    jd_file_id: string | null;
    jd_text: string | null;
    additional_notes: string | null;
  };
  payment: {
    status: string;
    amount_paise: number;
    currency: string;
    paid_at: string | null;
  };
  sla: {
    contact_status: string;
    contact_deadline_at: string | null;
    first_contacted_at: string | null;
  };
  schedule: {
    id: string;
    status: string;
    scheduled_start: string | null;
    scheduled_end: string | null;
    scheduled_duration_minutes: number | null;
    meeting_platform: string;
    meeting_url: string;
    joining_instructions: string | null;
    events: Array<any>;
    feedback: any;
  } | null;
  contact_logs: Array<{
    id: string;
    channel: string;
    notes: string;
    contacted_at: string;
  }>;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);

  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [slaFilter, setSlaFilter] = useState("all");

  // Selected Booking for Modal Actions
  const [selectedBooking, setSelectedBooking] = useState<BookingDetail | null>(null);
  const [modalMode, setModalMode] = useState<"detail" | "contact" | "schedule" | "reschedule" | "complete" | "cancel" | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Modal Form States
  const [contactNotes, setContactNotes] = useState("");
  const [schedStart, setSchedStart] = useState("");
  const [schedEnd, setSchedEnd] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [joiningInstructions, setJoiningInstructions] = useState("");
  const [reschedReason, setReschedReason] = useState("");

  // Feedback Form State
  const [strengths, setStrengths] = useState("");
  const [areasForImprovement, setAreasForImprovement] = useState("");
  const [techRating, setTechRating] = useState(4);
  const [commRating, setCommRating] = useState(4);
  const [recommendation, setRecommendation] = useState("");
  const [shareWithCandidate, setShareWithCandidate] = useState(true);

  // Cancellation State
  const [cancelReason, setCancelReason] = useState("");
  const [initiateRefund, setInitiateRefund] = useState(true);

  // Load User & Overview
  useEffect(() => {
    apiClient<{ user: User }>("/api/v1/auth/me")
      .then((res) => {
        if (res.user.role !== "ADMIN") {
          router.push("/dashboard");
          return;
        }
        setCurrentUser(res.user);
        loadData();
      })
      .catch(() => router.push("/login"));
  }, [router]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [ovData, bkData] = await Promise.all([
        apiClient<AdminOverview>("/api/v1/admin/overview"),
        apiClient<{ items: BookingItem[]; total: number }>(
          `/api/v1/admin/bookings?search=${encodeURIComponent(searchTerm)}&status=${statusFilter}&category_slug=${categoryFilter}&sla_filter=${slaFilter}`
        ),
      ]);
      setOverview(ovData);
      setBookings(bkData.items);
      setTotalCount(bkData.total);
    } catch (err: any) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, statusFilter, categoryFilter, slaFilter]);

  useEffect(() => {
    if (currentUser) {
      const timer = setTimeout(() => {
        loadData();
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [currentUser, searchTerm, statusFilter, categoryFilter, slaFilter, loadData]);

  const openBookingModal = async (bookingId: string, mode: "detail" | "contact" | "schedule" | "reschedule" | "complete" | "cancel") => {
    try {
      setActionError(null);
      const detail = await apiClient<BookingDetail>(`/api/v1/admin/bookings/${bookingId}`);
      setSelectedBooking(detail);
      setModalMode(mode);

      // Pre-fill fields for scheduling if present
      if (detail.schedule) {
        if (detail.schedule.scheduled_start) {
          setSchedStart(new Date(detail.schedule.scheduled_start).toISOString().slice(0, 16));
        }
        if (detail.schedule.scheduled_end) {
          setSchedEnd(new Date(detail.schedule.scheduled_end).toISOString().slice(0, 16));
        }
        setMeetingUrl(detail.schedule.meeting_url || "");
        setJoiningInstructions(detail.schedule.joining_instructions || "");
      } else {
        // Default tomorrow 4:00 PM IST
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(16, 0, 0, 0);
        const endTom = new Date(tomorrow.getTime() + 50 * 60000);
        setSchedStart(tomorrow.toISOString().slice(0, 16));
        setSchedEnd(endTom.toISOString().slice(0, 16));
        setMeetingUrl("https://meet.google.com/new");
        setJoiningInstructions(
          "Please join 5 minutes early using a laptop/desktop with working camera & microphone. Have your preferred coding environment ready."
        );
      }
    } catch (err: any) {
      alert("Failed to load booking details: " + (err.message || "Unknown error"));
    }
  };

  const handleRecordContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient(`/api/v1/admin/bookings/${selectedBooking.id}/contact`, {
        method: "POST",
        body: JSON.stringify({ channel: "EMAIL", notes: contactNotes }),
      });
      setModalMode(null);
      setContactNotes("");
      loadData();
    } catch (err: any) {
      setActionError(err.message || "Failed to record contact");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;

    // Validate 45 to 60 mins duration
    const start = new Date(schedStart);
    const end = new Date(schedEnd);
    const durationMin = (end.getTime() - start.getTime()) / 60000;
    if (durationMin < 45 || durationMin > 60) {
      setActionError(`Duration must be strictly between 45 and 60 minutes. Current: ${durationMin} minutes.`);
      return;
    }

    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient(`/api/v1/admin/bookings/${selectedBooking.id}/schedule`, {
        method: "POST",
        body: JSON.stringify({
          scheduled_start: start.toISOString(),
          scheduled_end: end.toISOString(),
          meeting_platform: "Google Meet",
          meeting_url: meetingUrl,
          joining_instructions: joiningInstructions,
        }),
      });
      setModalMode(null);
      loadData();
    } catch (err: any) {
      setActionError(err.message || "Scheduling conflict or server error");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReschedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;

    const start = new Date(schedStart);
    const end = new Date(schedEnd);
    const durationMin = (end.getTime() - start.getTime()) / 60000;
    if (durationMin < 45 || durationMin > 60) {
      setActionError(`Duration must be strictly between 45 and 60 minutes. Current: ${durationMin} minutes.`);
      return;
    }

    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient(`/api/v1/admin/bookings/${selectedBooking.id}/reschedule`, {
        method: "POST",
        body: JSON.stringify({
          scheduled_start: start.toISOString(),
          scheduled_end: end.toISOString(),
          meeting_url: meetingUrl,
          reason: reschedReason,
        }),
      });
      setModalMode(null);
      loadData();
    } catch (err: any) {
      setActionError(err.message || "Rescheduling error");
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient(`/api/v1/admin/bookings/${selectedBooking.id}/complete`, {
        method: "POST",
        body: JSON.stringify({
          strengths,
          areas_for_improvement: areasForImprovement,
          technical_rating: Number(techRating),
          communication_rating: Number(commRating),
          recommendation_summary: recommendation,
          is_shared_with_candidate: shareWithCandidate,
        }),
      });
      setModalMode(null);
      loadData();
    } catch (err: any) {
      setActionError(err.message || "Failed to submit completion feedback");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient(`/api/v1/admin/bookings/${selectedBooking.id}/cancel`, {
        method: "POST",
        body: JSON.stringify({
          reason: cancelReason,
          initiate_refund: initiateRefund,
        }),
      });
      setModalMode(null);
      loadData();
    } catch (err: any) {
      setActionError(err.message || "Failed to cancel booking");
    } finally {
      setActionLoading(false);
    }
  };

  if (!currentUser) return null;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      {/* Top Banner */}
      <div className="bg-slate-900 text-white border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Single Interviewer Operations Console
              </span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight mt-1 text-white">
              Interviewer & Admin Dashboard
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Timezone: <strong className="text-slate-200">Asia/Kolkata (IST)</strong> &bull; Same-day contact SLA guarantee
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadData}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Refresh Metrics</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
              <span>Total Revenue</span>
              <TrendingUp className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="mt-3">
              <div className="text-2xl font-black text-slate-900">
                ₹{overview ? overview.total_revenue_inr.toLocaleString("en-IN") : "0"}
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {overview ? overview.total_revenue_paise / 19900 : 0} paid sessions (₹199 each)
              </div>
            </div>
          </div>

          <div
            className={`p-5 rounded-xl border shadow-sm flex flex-col justify-between ${
              overview && overview.awaiting_contact_count > 0
                ? "bg-amber-50 border-amber-200"
                : "bg-white border-slate-200"
            }`}
          >
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-600 flex items-center justify-between">
              <span>Awaiting Contact</span>
              <Clock className="w-4 h-4 text-amber-600" />
            </div>
            <div className="mt-3">
              <div className="text-2xl font-black text-amber-900">
                {overview?.awaiting_contact_count || 0}
              </div>
              <div className="text-xs text-amber-700 font-medium mt-1">
                Must email candidates today
              </div>
            </div>
          </div>

          <div
            className={`p-5 rounded-xl border shadow-sm flex flex-col justify-between ${
              overview && overview.overdue_contact_count > 0
                ? "bg-rose-50 border-rose-300 animate-pulse"
                : "bg-white border-slate-200"
            }`}
          >
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-600 flex items-center justify-between">
              <span>Overdue SLA</span>
              <ShieldAlert className="w-4 h-4 text-rose-600" />
            </div>
            <div className="mt-3">
              <div className="text-2xl font-black text-rose-900">
                {overview?.overdue_contact_count || 0}
              </div>
              <div className="text-xs text-rose-700 font-semibold mt-1">
                Breached same-day deadline
              </div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
              <span>Scheduled</span>
              <Calendar className="w-4 h-4 text-sky-600" />
            </div>
            <div className="mt-3">
              <div className="text-2xl font-black text-slate-900">
                {overview?.scheduled_count || 0}
              </div>
              <div className="text-xs text-slate-500 mt-1">45–60 min sessions</div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
              <span>Completed</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="mt-3">
              <div className="text-2xl font-black text-slate-900">
                {overview?.completed_count || 0}
              </div>
              <div className="text-xs text-slate-500 mt-1">Successfully conducted</div>
            </div>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col lg:flex-row items-center justify-between gap-4">
          <div className="relative w-full lg:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search candidate, email, or MOCK- ref..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="">All Categories (6)</option>
              <option value="system-design">System Design</option>
              <option value="dsa">DSA</option>
              <option value="ai-engineer">AI Engineer</option>
              <option value="full-stack">Full Stack</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
            </select>

            <select
              value={slaFilter}
              onChange={(e) => setSlaFilter(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="all">All Contact SLAs</option>
              <option value="pending">Awaiting Contact</option>
              <option value="overdue">Overdue Contact Only</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="">All Statuses</option>
              <option value="PAID_AWAITING_CONTACT">Awaiting Contact</option>
              <option value="CONTACTED">Contacted</option>
              <option value="SCHEDULED">Scheduled</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Bookings Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-bold text-slate-900 text-base">Candidate Bookings ({totalCount})</h2>
            <span className="text-xs text-slate-500">Filtered View</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-xs uppercase font-bold text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Reference & Category</th>
                  <th className="px-6 py-3">Candidate</th>
                  <th className="px-6 py-3">Payment</th>
                  <th className="px-6 py-3">Contact SLA</th>
                  <th className="px-6 py-3">Interview Slot</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {bookings.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                      No interview bookings found matching the current filters.
                    </td>
                  </tr>
                ) : (
                  bookings.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50/75 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-mono font-bold text-xs text-sky-700 bg-sky-50 inline-block px-2 py-0.5 rounded">
                          {b.booking_reference}
                        </div>
                        <div className="font-semibold text-slate-900 mt-1">{b.category_title}</div>
                        <div className="text-xs text-slate-400">45–60 minutes</div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900">{b.candidate_name}</div>
                        <div className="text-xs text-slate-500">{b.candidate_email}</div>
                        <div className="text-xs text-slate-400">{b.candidate_phone}</div>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                            b.payment_status === "CAPTURED"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-slate-100 text-slate-600"
                          }`}
                        >
                          {b.payment_status} (₹199)
                        </span>
                      </td>

                      <td className="px-6 py-4">
                        {b.contact_status === "CONTACTED" ? (
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>Contacted</span>
                          </div>
                        ) : (
                          <div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800">
                              Awaiting Contact
                            </span>
                            {b.contact_deadline_at && (
                              <div className="text-[11px] text-slate-500 mt-1">
                                Deadline: {new Date(b.contact_deadline_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                              </div>
                            )}
                          </div>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        {b.scheduled_start ? (
                          <div>
                            <div className="text-xs font-semibold text-slate-900">
                              {new Date(b.scheduled_start).toLocaleDateString("en-IN", {
                                weekday: "short",
                                day: "numeric",
                                month: "short",
                              })}
                            </div>
                            <div className="text-xs text-slate-500">
                              {new Date(b.scheduled_start).toLocaleTimeString("en-IN", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}{" "}
                              IST
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 italic">Not yet assigned</span>
                        )}
                      </td>

                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openBookingModal(b.id, "detail")}
                            className="px-2.5 py-1 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded transition-colors"
                          >
                            Dossier
                          </button>

                          {b.contact_status !== "CONTACTED" && (
                            <button
                              onClick={() => openBookingModal(b.id, "contact")}
                              className="px-2.5 py-1 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded transition-colors"
                            >
                              Log Contact
                            </button>
                          )}

                          {!b.scheduled_start && b.payment_status === "CAPTURED" && (
                            <button
                              onClick={() => openBookingModal(b.id, "schedule")}
                              className="px-2.5 py-1 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded transition-colors"
                            >
                              Schedule
                            </button>
                          )}

                          {b.scheduled_start && b.scheduling_status === "SCHEDULED" && (
                            <>
                              <button
                                onClick={() => openBookingModal(b.id, "complete")}
                                className="px-2.5 py-1 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded transition-colors"
                              >
                                Complete
                              </button>
                              <button
                                onClick={() => openBookingModal(b.id, "reschedule")}
                                className="px-2 py-1 text-xs text-slate-600 hover:text-slate-900 rounded"
                              >
                                Shift
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ACTION MODALS */}
      {modalMode && selectedBooking && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white">
              <div>
                <span className="font-mono text-xs font-bold text-sky-600">
                  {selectedBooking.booking_reference}
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-0.5">
                  {modalMode === "detail" && "Candidate Dossier & Audit"}
                  {modalMode === "contact" && "Log Personal Outreach Contact"}
                  {modalMode === "schedule" && "Schedule Interview (45–60 min)"}
                  {modalMode === "reschedule" && "Reschedule Interview"}
                  {modalMode === "complete" && "Complete Session & Evaluation"}
                  {modalMode === "cancel" && "Cancel Booking & Refund"}
                </h3>
              </div>
              <button
                onClick={() => setModalMode(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            {/* Error Message */}
            {actionError && (
              <div className="mx-6 mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{actionError}</span>
              </div>
            )}

            {/* Modal Body */}
            <div className="p-6">
              {/* DOSSIER VIEW */}
              {modalMode === "detail" && (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                      Candidate Profile
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-sm bg-slate-50 p-4 rounded-lg">
                      <div>
                        <span className="text-slate-500 text-xs block">Full Name</span>
                        <span className="font-semibold">{selectedBooking.candidate.full_name}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-xs block">Email Address</span>
                        <a href={`mailto:${selectedBooking.candidate.email}`} className="text-sky-600 font-medium">
                          {selectedBooking.candidate.email}
                        </a>
                      </div>
                      <div>
                        <span className="text-slate-500 text-xs block">Phone</span>
                        <span className="font-semibold">{selectedBooking.candidate.phone}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-xs block">Total Experience</span>
                        <span className="font-semibold">
                          {selectedBooking.professional_input.years_experience} Years
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-xs block">Current/Past Company</span>
                        <span className="font-semibold">
                          {selectedBooking.professional_input.current_company || "Not specified"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-xs block">Target Role</span>
                        <span className="font-semibold">
                          {selectedBooking.professional_input.target_role || "Not specified"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                      Candidate Resume & JD
                    </h4>
                    <div className="flex gap-3">
                      {selectedBooking.professional_input.resume_file_id && (
                        <a
                          href={`/api/v1/candidate/files/${selectedBooking.professional_input.resume_file_id}`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 text-xs font-semibold"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>Download Resume (PDF/DOCX)</span>
                        </a>
                      )}
                    </div>
                    {selectedBooking.professional_input.jd_text && (
                      <div className="mt-3">
                        <span className="text-slate-500 text-xs block mb-1">Target Job Description</span>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 max-h-40 overflow-y-auto whitespace-pre-wrap font-sans">
                          {selectedBooking.professional_input.jd_text}
                        </div>
                      </div>
                    )}
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                      Contact History Logs
                    </h4>
                    {selectedBooking.contact_logs.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">No contact logs recorded yet.</p>
                    ) : (
                      <div className="space-y-2">
                        {selectedBooking.contact_logs.map((log) => (
                          <div key={log.id} className="p-3 rounded bg-slate-50 border border-slate-200 text-xs">
                            <div className="flex justify-between font-semibold text-slate-800">
                              <span>Outreach via {log.channel}</span>
                              <span className="text-slate-500">{new Date(log.contacted_at).toLocaleString("en-IN")}</span>
                            </div>
                            <p className="text-slate-600 mt-1">{log.notes}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* LOG CONTACT FORM */}
              {modalMode === "contact" && (
                <form onSubmit={handleRecordContact} className="space-y-4">
                  <p className="text-xs text-slate-600">
                    Record your direct email outreach to candidate <strong>{selectedBooking.candidate.email}</strong>.
                    This fulfills the same-day contact SLA requirement.
                  </p>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Outreach Notes
                    </label>
                    <textarea
                      required
                      rows={4}
                      value={contactNotes}
                      onChange={(e) => setContactNotes(e.target.value)}
                      placeholder="e.g. Sent introductory email inquiring about candidate availability for this weekend."
                      className="w-full p-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setModalMode(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow-sm disabled:opacity-50"
                    >
                      {actionLoading ? "Saving..." : "Record Contact & Satisfy SLA"}
                    </button>
                  </div>
                </form>
              )}

              {/* SCHEDULE INTERVIEW FORM */}
              {modalMode === "schedule" && (
                <form onSubmit={handleSchedule} className="space-y-4">
                  <div className="p-3 bg-sky-50 border border-sky-100 rounded-lg text-xs text-sky-800">
                    <strong>Rule:</strong> The interview duration must be between <strong>45 and 60 minutes</strong>.
                    Overlapping interviews are prevented by the backend.
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        Start Time (IST)
                      </label>
                      <input
                        type="datetime-local"
                        required
                        value={schedStart}
                        onChange={(e) => setSchedStart(e.target.value)}
                        className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        End Time (IST)
                      </label>
                      <input
                        type="datetime-local"
                        required
                        value={schedEnd}
                        onChange={(e) => setSchedEnd(e.target.value)}
                        className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Meeting URL (Google Meet / Zoom)
                    </label>
                    <input
                      type="url"
                      required
                      value={meetingUrl}
                      onChange={(e) => setMeetingUrl(e.target.value)}
                      placeholder="https://meet.google.com/abc-defg-hij"
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Joining Instructions
                    </label>
                    <textarea
                      rows={3}
                      value={joiningInstructions}
                      onChange={(e) => setJoiningInstructions(e.target.value)}
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setModalMode(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold shadow-sm disabled:opacity-50"
                    >
                      {actionLoading ? "Scheduling..." : "Confirm & Send Calendar Invite"}
                    </button>
                  </div>
                </form>
              )}

              {/* RESCHEDULE FORM */}
              {modalMode === "reschedule" && (
                <form onSubmit={handleReschedule} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        New Start (IST)
                      </label>
                      <input
                        type="datetime-local"
                        required
                        value={schedStart}
                        onChange={(e) => setSchedStart(e.target.value)}
                        className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        New End (IST)
                      </label>
                      <input
                        type="datetime-local"
                        required
                        value={schedEnd}
                        onChange={(e) => setSchedEnd(e.target.value)}
                        className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Reason for Rescheduling
                    </label>
                    <input
                      type="text"
                      required
                      value={reschedReason}
                      onChange={(e) => setReschedReason(e.target.value)}
                      placeholder="e.g. Coordinated mutually over email due to candidate exam"
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setModalMode(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-sm disabled:opacity-50"
                    >
                      {actionLoading ? "Updating..." : "Reschedule & Notify Candidate"}
                    </button>
                  </div>
                </form>
              )}

              {/* COMPLETE SESSION FORM */}
              {modalMode === "complete" && (
                <form onSubmit={handleComplete} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        Technical Rating (1–5)
                      </label>
                      <select
                        value={techRating}
                        onChange={(e) => setTechRating(Number(e.target.value))}
                        className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                      >
                        <option value={1}>1 - Needs Significant Work</option>
                        <option value={2}>2 - Below Bar</option>
                        <option value={3}>3 - Approaching Bar</option>
                        <option value={4}>4 - Solid Pass (Hire)</option>
                        <option value={5}>5 - Strong Hire (Exceptional)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                        Communication Rating (1–5)
                      </label>
                      <select
                        value={commRating}
                        onChange={(e) => setCommRating(Number(e.target.value))}
                        className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                      >
                        <option value={1}>1 - Poor / Unclear</option>
                        <option value={2}>2 - Weak articulation</option>
                        <option value={3}>3 - Good</option>
                        <option value={4}>4 - Clear & Structured</option>
                        <option value={5}>5 - Executive Level</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Technical Strengths
                    </label>
                    <textarea
                      required
                      rows={3}
                      value={strengths}
                      onChange={(e) => setStrengths(e.target.value)}
                      placeholder="Key strengths demonstrated during the 45-60 min session..."
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Areas For Improvement
                    </label>
                    <textarea
                      required
                      rows={3}
                      value={areasForImprovement}
                      onChange={(e) => setAreasForImprovement(e.target.value)}
                      placeholder="Constructive action points and topics to study..."
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                      Recommendation Summary
                    </label>
                    <input
                      type="text"
                      required
                      value={recommendation}
                      onChange={(e) => setRecommendation(e.target.value)}
                      placeholder="e.g. Recommended for Mid-to-Senior Full Stack roles after practicing concurrency."
                      className="w-full p-2.5 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <input
                      type="checkbox"
                      id="shareFeedback"
                      checked={shareWithCandidate}
                      onChange={(e) => setShareWithCandidate(e.target.checked)}
                      className="rounded border-slate-300 text-sky-600"
                    />
                    <label htmlFor="shareFeedback" className="text-xs text-slate-700 font-medium">
                      Share evaluation notes on candidate dashboard
                    </label>
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setModalMode(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm disabled:opacity-50"
                    >
                      {actionLoading ? "Submitting..." : "Complete & Save Feedback"}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
