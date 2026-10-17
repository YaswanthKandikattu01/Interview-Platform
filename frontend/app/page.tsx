import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  ShieldCheck,
  Clock,
  CheckCircle2,
  ArrowRight,
  Cpu,
  Code2,
  Sparkles,
  Layers,
  Layout,
  Server,
  CalendarX2,
  Video,
  FileText,
} from "lucide-react";

const CATEGORIES = [
  {
    slug: "system-design",
    title: "System Design Mock Interview",
    description: "Deep dive into scalability, microservices, distributed caching, database sharding, and architecture trade-offs.",
    topics: ["High-Level Design", "Distributed Systems", "Database Sharding", "Caching Strategies", "Load Balancing"],
    icon: Layers,
    color: "from-sky-500/20 to-indigo-500/20 text-sky-600 dark:text-sky-400",
    price: "₹499",
    duration: "2 Hours (120 mins)",
    featured: true,
    tag: "Extended Deep Dive",
  },
  {
    slug: "resume-review",
    title: "Resume Review & Career Strategy",
    description: "Detailed line-by-line ATS resume critique, impactful bullet-point rephrasing, and role-specific positioning.",
    topics: ["ATS Optimization", "Quantified Bullet Points", "Project Framing", "Skills Alignment", "Actionable Next Steps"],
    icon: FileText,
    color: "from-emerald-500/20 to-teal-500/20 text-emerald-600 dark:text-emerald-400",
    price: "₹119",
    duration: "Detailed Review & Feedback",
    featured: false,
    tag: "Career Booster",
  },
  {
    slug: "dsa",
    title: "DSA Mock Interview",
    description: "Data structures, algorithms, problem decomposition, optimal time/space complexity, and clean code under pressure.",
    topics: ["Dynamic Programming", "Graphs & Trees", "Binary Search", "Heaps & Hash Tables", "Time Complexity"],
    icon: Code2,
    color: "from-amber-500/20 to-orange-500/20 text-amber-600 dark:text-amber-400",
    price: "₹199",
    duration: "45–60 minutes",
    featured: false,
  },
  {
    slug: "ai-engineer",
    title: "AI Engineer Mock Interview",
    description: "LLM system design, RAG pipelines, prompt engineering, vector databases, and production model evaluation.",
    topics: ["RAG Architecture", "Vector Embeddings & Search", "Fine-Tuning vs Prompting", "Agent Workflows", "Guardrails & Evals"],
    icon: Sparkles,
    color: "from-purple-500/20 to-pink-500/20 text-purple-600 dark:text-purple-400",
    price: "₹199",
    duration: "45–60 minutes",
    featured: false,
  },
  {
    slug: "full-stack",
    title: "Full Stack Mock Interview",
    description: "End-to-end web engineering, frontend performance, robust backend APIs, and database patterns.",
    topics: ["REST & GraphQL APIs", "Full-Stack Security", "State Management", "Data Modeling", "Web Vitals & Performance"],
    icon: Cpu,
    color: "from-cyan-500/20 to-blue-500/20 text-cyan-600 dark:text-cyan-400",
    price: "₹199",
    duration: "45–60 minutes",
    featured: false,
  },
  {
    slug: "frontend",
    title: "Frontend Mock Interview",
    description: "Modern React, Next.js architecture, TypeScript, responsive UX, accessibility, and browser performance.",
    topics: ["React & Component Design", "Rendering Strategies (SSR/SSG)", "Accessibility (a11y)", "Browser Performance", "State Architecture"],
    icon: Layout,
    color: "from-blue-500/20 to-sky-500/20 text-blue-600 dark:text-blue-400",
    price: "₹199",
    duration: "45–60 minutes",
    featured: false,
  },
  {
    slug: "backend",
    title: "Backend Mock Interview",
    description: "Concurrency, API resilience, relational/NoSQL schemas, caching, queues, and security.",
    topics: ["API Design & REST", "SQL & Database Indexing", "Message Queues & Event-Driven", "Authentication & Security", "Performance Profiling"],
    icon: Server,
    color: "from-rose-500/20 to-red-500/20 text-rose-600 dark:text-rose-400",
    price: "₹199",
    duration: "45–60 minutes",
    featured: false,
  },
];

const FAQS = [
  {
    question: "Why can't I choose an interview date and time on the website?",
    answer: "We intentionally do not use automated availability calendars or slot countdowns. Every mock interview is personally conducted by a senior technical interviewer. After completing your payment, our interviewer contacts you directly by email on the same calendar day to coordinate a mutually convenient date and time."
  },
  {
    question: "How does the same-day contact promise work?",
    answer: "For all bookings completed between 08:00 AM IST and 08:00 PM IST (Asia/Kolkata), our interviewer personally emails you by 11:59 PM IST on the same calendar day. If you book after 08:00 PM IST, you will receive personal outreach by 12:00 PM IST the following morning."
  },
  {
    question: "What is the duration and price for each session?",
    answer: "Our System Design Mock Interview is an extended 2-hour deep dive at ₹499. The Resume Review service is ₹119 for a comprehensive line-by-line review. All technical mock interviews (DSA, AI, Full Stack, Frontend, Backend) are 45–60 minutes at ₹199 flat."
  },
  {
    question: "How do I attend the interview?",
    answer: "Once the date and time are mutually agreed via email, you will receive a calendar invitation containing either a Google Meet or Zoom video link with joining instructions."
  },
  {
    question: "What if I need to reschedule or cancel?",
    answer: "If you notify us at least 12 hours prior to your scheduled interview, you are eligible for a 100% refund or a free reschedule. If our team ever fails to meet the same-day contact SLA window, an automatic full refund is guaranteed."
  }
];

export default function HomePage() {
  return (
    <>
      <Navbar />

      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-16 pb-20 sm:pt-24 sm:pb-28 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-b from-white via-slate-50/50 to-slate-100/50 dark:from-slate-950 dark:via-slate-900/40 dark:to-slate-950 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-900 dark:text-amber-300 mb-8 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span>100% Real Human Interviewer • Affordable Tech Mentorship</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto mb-6 leading-tight">
            Prepare Smarter. <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-sky-600 to-indigo-600 dark:from-sky-400 dark:to-indigo-400 bg-clip-text text-transparent">
              Perform Better.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            Practice real technical interviews with a senior software engineer. No bots, no AI scripts. Get candid feedback on System Design, DSA, AI, Full Stack, Frontend, Backend, or a targeted Resume Review.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-16">
            <Link
              href="#categories"
              className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-3.5 rounded-xl text-base font-bold text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 shadow-lg shadow-slate-900/10 transition-all"
            >
              Explore Programs & Book
            </Link>
            <Link
              href="#pricing"
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-xl text-base font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 shadow-sm transition-all"
            >
              View Transparent Pricing
            </Link>
          </div>

          {/* Trust Guarantees */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto pt-8 border-t border-slate-200/60 dark:border-slate-800/60 text-left">
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-sky-600 dark:text-sky-400 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200">100% Human Interviewer</span>
            </div>
            <div className="flex items-center gap-2.5">
              <Clock className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200">Same-Day Contact</span>
            </div>
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200">Deep Dive Evaluation</span>
            </div>
            <div className="flex items-center gap-2.5">
              <Video className="w-5 h-5 text-purple-600 dark:text-purple-400 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200">Google Meet / Zoom</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. PROGRAMS & INTERVIEW CATEGORIES */}
      <section id="categories" className="py-20 sm:py-28 bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-widest mb-3">
              Specialized Programs
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              Choose Your Mock Interview Track
            </h3>
            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300">
              Each session is conducted 1-on-1 by an experienced engineering interviewer tailored directly to your resume and career objectives.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {CATEGORIES.map((cat) => {
              const Icon = cat.icon;
              return (
                <div
                  key={cat.slug}
                  className={`flex flex-col bg-slate-50/70 dark:bg-slate-900/60 border rounded-2xl p-6 transition-all relative group ${
                    cat.featured
                      ? "border-sky-500/60 dark:border-sky-500/50 shadow-md ring-1 ring-sky-500/20"
                      : "border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-xl"
                  }`}
                >
                  {cat.tag && (
                    <div className="absolute -top-3 right-5 bg-sky-600 dark:bg-sky-500 text-white text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow-sm">
                      {cat.tag}
                    </div>
                  )}

                  {/* Category Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cat.color} flex items-center justify-center`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-extrabold text-slate-900 dark:text-white">{cat.price}</span>
                      <span className="block text-[11px] text-slate-500 dark:text-slate-400 font-medium">Flat Fee</span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2 group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors">
                    {cat.title}
                  </h4>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mb-6 leading-relaxed flex-1">
                    {cat.description}
                  </p>

                  {/* Duration Tag */}
                  <div className="flex items-center gap-2 mb-4 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 w-fit">
                    <Clock className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
                    <span>Duration: {cat.duration}</span>
                  </div>

                  {/* Key Topics */}
                  <div className="mb-6">
                    <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider block mb-2">
                      Key Evaluation Areas:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {cat.topics.map((t, idx) => (
                        <span
                          key={idx}
                          className="text-xs font-medium bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 px-2.5 py-1 rounded-md"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Book CTA */}
                  <Link
                    href={`/book/${cat.slug}`}
                    className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 shadow-sm transition-all mt-auto"
                  >
                    <span>Book Now — {cat.price}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 3. TRANSPARENT PRICING TIERS */}
      <section id="pricing" className="py-20 sm:py-28 bg-slate-50 dark:bg-slate-900/40 border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-widest mb-3">
              Transparent Pricing
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              Simple, Honest Investment in Your Career
            </h3>
            <p className="text-slate-600 dark:text-slate-300">
              High-impact engineering prep priced affordably for real developers across India.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
            {/* Tier 1: Resume Review */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 shadow-sm flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block mb-1">
                  Document Audit
                </span>
                <h4 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Resume Review</h4>
                <div className="flex items-baseline gap-1 my-4">
                  <span className="text-4xl font-black text-slate-900 dark:text-white">₹119</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">flat fee</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
                  Comprehensive line-by-line ATS resume critique and career strategy notes.
                </p>
                <div className="space-y-2.5 text-xs text-slate-700 dark:text-slate-300 mb-6">
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>ATS keywords & format evaluation</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Quantified impact rephrasing</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Role targeting recommendations</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Actionable written improvement dossier</span></div>
                </div>
              </div>
              <Link
                href="/book/resume-review"
                className="w-full text-center py-3 rounded-xl font-bold text-xs uppercase tracking-wider text-slate-900 dark:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                Book Resume Review — ₹119
              </Link>
            </div>

            {/* Tier 2: Standard Mock Interview (₹199) */}
            <div className="bg-white dark:bg-slate-900 border-2 border-slate-900 dark:border-sky-500 rounded-3xl p-8 shadow-xl flex flex-col justify-between relative">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-slate-900 dark:bg-sky-500 text-white text-[10px] font-extrabold uppercase tracking-widest px-4 py-1 rounded-full shadow">
                Most Popular
              </div>
              <div>
                <span className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-wider block mb-1">
                  1-on-1 Human Session
                </span>
                <h4 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Technical Mock Interview</h4>
                <div className="flex items-baseline gap-1 my-4">
                  <span className="text-4xl font-black text-slate-900 dark:text-white">₹199</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">all-inclusive</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
                  DSA, AI Engineer, Full Stack, Frontend, or Backend. 45–60 minutes live video interview.
                </p>
                <div className="space-y-2.5 text-xs text-slate-700 dark:text-slate-300 mb-6">
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Real human senior software engineer</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>45–60 min live technical grilling</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Tailored to your specific resume & role</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Same-day scheduling email outreach</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Candid feedback on strengths & gaps</span></div>
                </div>
              </div>
              <Link
                href="#categories"
                className="w-full text-center py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider text-white bg-slate-900 dark:bg-sky-600 hover:bg-slate-800 dark:hover:bg-sky-500 transition-colors shadow-md"
              >
                Choose Track — ₹199
              </Link>
            </div>

            {/* Tier 3: System Design Deep Dive (₹499) */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 shadow-sm flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block mb-1">
                  Architecture Intensive
                </span>
                <h4 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">System Design (2 Hours)</h4>
                <div className="flex items-baseline gap-1 my-4">
                  <span className="text-4xl font-black text-slate-900 dark:text-white">₹499</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">all-inclusive</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
                  Full 2-hour architectural deep dive for Mid/Senior/Staff engineering positions.
                </p>
                <div className="space-y-2.5 text-xs text-slate-700 dark:text-slate-300 mb-6">
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>2 Hours (120 mins) live whiteboarding</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>HLD + LLD component modeling</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Sharding, caching, CAP theorem trade-offs</span></div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /><span>Comprehensive architectural feedback</span></div>
                </div>
              </div>
              <Link
                href="/book/system-design"
                className="w-full text-center py-3 rounded-xl font-bold text-xs uppercase tracking-wider text-slate-900 dark:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                Book System Design — ₹499
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS */}
      <section id="how-it-works" className="py-20 sm:py-28 bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-widest mb-3">
              Simple Journey
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              How Your Mock Interview Works
            </h3>
            <p className="text-slate-600 dark:text-slate-300">
              No complicated calendars or expired temporary slot holds. Seamless, human-coordinated scheduling.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800">
              <div className="w-10 h-10 rounded-full bg-slate-900 dark:bg-sky-600 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                1
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white mb-2">Choose Program</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Select your preferred technical interview track or resume review.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800">
              <div className="w-10 h-10 rounded-full bg-slate-900 dark:bg-sky-600 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                2
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white mb-2">Enter Details & Resume</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Provide your name, email, optional phone number, resume, and any suggestions for the interviewer.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800">
              <div className="w-10 h-10 rounded-full bg-slate-900 dark:bg-sky-600 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                3
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white mb-2">Instant Secure Checkout</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Pay securely via UPI, Cards, or Netbanking. Zero hidden fees.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800">
              <div className="w-10 h-10 rounded-full bg-slate-900 dark:bg-sky-600 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                4
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white mb-2">Same-Day Outreach</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Interviewer personally emails you today to coordinate your Google Meet / Zoom session.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. FAQS */}
      <section id="faqs" className="py-20 sm:py-28 bg-slate-50 dark:bg-slate-900/40 border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-widest mb-3">
              Frequently Asked Questions
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Everything You Need to Know
            </h3>
          </div>

          <div className="space-y-4">
            {FAQS.map((faq, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
              >
                <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                  {faq.question}
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
