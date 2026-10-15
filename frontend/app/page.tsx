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
  HelpCircle,
  CalendarX2,
  Video,
} from "lucide-react";

const CATEGORIES = [
  {
    slug: "system-design",
    title: "System Design Mock Interview",
    description: "Scalability, microservices, distributed caching, database sharding, and architecture trade-offs.",
    topics: ["High-Level Design", "Distributed Systems", "Database Sharding", "Caching Strategies", "Load Balancing"],
    icon: Layers,
    color: "from-sky-500/10 to-indigo-500/10 text-sky-600",
  },
  {
    slug: "dsa",
    title: "DSA Mock Interview",
    description: "Data structures, algorithms, problem decomposition, optimal time/space complexity, and clean code.",
    topics: ["Dynamic Programming", "Graphs & Trees", "Binary Search", "Heaps & Hash Tables", "Time Complexity"],
    icon: Code2,
    color: "from-emerald-500/10 to-teal-500/10 text-emerald-600",
  },
  {
    slug: "ai-engineer",
    title: "AI Engineer Mock Interview",
    description: "LLM system design, RAG pipelines, prompt engineering, vector databases, and model evaluation.",
    topics: ["RAG Architecture", "Vector Embeddings & Search", "Fine-Tuning vs Prompting", "Agent Workflows", "Guardrails & Evals"],
    icon: Sparkles,
    color: "from-purple-500/10 to-pink-500/10 text-purple-600",
  },
  {
    slug: "full-stack",
    title: "Full Stack Mock Interview",
    description: "End-to-end web engineering, frontend performance, robust backend APIs, and database patterns.",
    topics: ["REST & GraphQL APIs", "Full-Stack Security", "State Management", "Data Modeling", "Web Vitals & Performance"],
    icon: Cpu,
    color: "from-amber-500/10 to-orange-500/10 text-amber-600",
  },
  {
    slug: "frontend",
    title: "Frontend Mock Interview",
    description: "Modern React, Next.js architecture, TypeScript, responsive UX, accessibility, and browser performance.",
    topics: ["React & Component Design", "Rendering Strategies (SSR/SSG)", "Accessibility (a11y)", "Browser Performance", "State Architecture"],
    icon: Layout,
    color: "from-blue-500/10 to-cyan-500/10 text-blue-600",
  },
  {
    slug: "backend",
    title: "Backend Mock Interview",
    description: "Concurrency, API resilience, relational/NoSQL schemas, caching, queues, and security.",
    topics: ["API Design & REST", "SQL & Database Indexing", "Message Queues & Event-Driven", "Authentication & Security", "Performance Profiling"],
    icon: Server,
    color: "from-rose-500/10 to-red-500/10 text-rose-600",
  },
];

const FAQS = [
  {
    question: "Why can't I choose an interview date and time on the website?",
    answer: "We intentionally do not use automated availability calendars or slot pickers. Every mock interview is personally conducted by a senior technical interviewer. After you pay ₹199, our interviewer contacts you directly by email on the same day to coordinate a mutually convenient date and time."
  },
  {
    question: "How does the same-day contact promise work?",
    answer: "For all bookings completed between 08:00 AM IST and 08:00 PM IST (Asia/Kolkata), our interviewer personally emails you by 11:59 PM IST on the same calendar day. If you book after 08:00 PM IST, you will receive personal outreach by 12:00 PM IST the following morning."
  },
  {
    question: "What is the duration of the mock interview?",
    answer: "Every mock interview is 45–60 minutes. The interviewer conducts a focused technical session tailored to your resume and target role, followed by actionable, constructive feedback on strengths and improvement areas."
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
      <section className="relative overflow-hidden pt-16 pb-20 sm:pt-24 sm:pb-28 border-b border-slate-200 bg-gradient-to-b from-white via-slate-50/50 to-slate-100/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-50 border border-amber-200 text-amber-900 mb-8 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span>100% Real Human Interviewer • ₹199 Flat Fee • 45–60 Mins</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 max-w-4xl mx-auto mb-6 leading-tight">
            Prepare Smarter. <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">
              Perform Better.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
            Practice real technical interviews with a senior software engineer. No bots, no AI scripts. Get candid feedback on System Design, DSA, AI, Full Stack, Frontend, or Backend.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-16">
            <Link
              href="#categories"
              className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-3.5 rounded-xl text-base font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-lg shadow-slate-900/10 transition-all"
            >
              Book Your Mock Interview — ₹199
            </Link>
            <Link
              href="#categories"
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-xl text-base font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 shadow-sm transition-all"
            >
              Explore Categories
            </Link>
          </div>

          {/* Trust Guarantees */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto pt-8 border-t border-slate-200/60 text-left">
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-sky-600 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800">100% Human Interviewer</span>
            </div>
            <div className="flex items-center gap-2.5">
              <Clock className="w-5 h-5 text-emerald-600 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800">Same-Day Contact</span>
            </div>
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800">45–60 Min Deep Dive</span>
            </div>
            <div className="flex items-center gap-2.5">
              <Video className="w-5 h-5 text-purple-600 shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-slate-800">Google Meet / Zoom</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. EXACTLY SIX INTERVIEW CATEGORIES */}
      <section id="categories" className="py-20 sm:py-28 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest mb-3">
              Specialized Tracks
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Choose Your Mock Interview Track
            </h3>
            <p className="text-base sm:text-lg text-slate-600">
              Each session is conducted by a seasoned engineering interviewer tailored to your resume, target role, and job description.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {CATEGORIES.map((cat) => {
              const Icon = cat.icon;
              return (
                <div
                  key={cat.slug}
                  className="flex flex-col bg-slate-50/70 border border-slate-200/80 rounded-2xl p-6 hover:shadow-xl hover:border-slate-300 transition-all relative group"
                >
                  {/* Category Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cat.color} flex items-center justify-center`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-extrabold text-slate-900">₹199</span>
                      <span className="block text-[11px] text-slate-500 font-medium">Flat Fee</span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h4 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-sky-600 transition-colors">
                    {cat.title}
                  </h4>
                  <p className="text-sm text-slate-600 mb-6 leading-relaxed flex-1">
                    {cat.description}
                  </p>

                  {/* Duration Tag */}
                  <div className="flex items-center gap-2 mb-4 text-xs font-semibold text-slate-700 bg-white px-3 py-1.5 rounded-lg border border-slate-200 w-fit">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Duration: 45–60 minutes</span>
                  </div>

                  {/* Key Topics */}
                  <div className="mb-6">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                      Key Evaluation Areas:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {cat.topics.map((t, idx) => (
                        <span
                          key={idx}
                          className="text-xs font-medium bg-white text-slate-700 border border-slate-200/80 px-2.5 py-1 rounded-md"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Book CTA */}
                  <Link
                    href={`/book/${cat.slug}`}
                    className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-sm transition-all mt-auto"
                  >
                    <span>Book Interview — ₹199</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 3. TRANSPARENT PRICING SECTION */}
      <section id="pricing" className="py-20 sm:py-28 bg-slate-50 border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest mb-3">
              One Transparent Package
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Simple, Honest Pricing. No Tiers. No Surprises.
            </h3>
            <p className="text-slate-600">
              We believe elite technical interview preparation should be accessible to all software engineers across India.
            </p>
          </div>

          <div className="bg-white border-2 border-slate-900 rounded-3xl p-8 sm:p-12 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider px-6 py-2 rounded-bl-2xl">
              Standard Package
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <span className="text-xs font-bold text-sky-600 uppercase tracking-wider block mb-1">
                  1-on-1 Human Mock Interview
                </span>
                <h4 className="text-3xl font-extrabold text-slate-900 mb-4">
                  45–60 Minute Session
                </h4>
                <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                  One-on-one live technical mock interview conducted by an experienced senior engineer. The interviewer coordinates scheduling directly with you via email on the same day.
                </p>

                <div className="space-y-3 mb-8">
                  <div className="flex items-center gap-3 text-sm text-slate-700">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                    <span>Real human senior software engineer (No AI bots)</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-700">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                    <span>Tailored to your specific resume & target job role</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-700">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                    <span>Same-day scheduling email outreach guarantee</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-700">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                    <span>Google Meet or Zoom invitation with calendar link</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-700">
                    <CalendarX2 className="w-5 h-5 text-slate-400 shrink-0" />
                    <span className="text-slate-500">No public calendar pickers or slot countdowns</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 text-center flex flex-col justify-center items-center">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Total Investment
                </span>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-5xl sm:text-6xl font-black text-slate-900">₹199</span>
                  <span className="text-sm font-semibold text-slate-500">all-inclusive</span>
                </div>
                <span className="text-xs text-slate-500 mb-6">
                  (Exactly 19,900 paise via Razorpay. Zero hidden fees.)
                </span>

                <Link
                  href="#categories"
                  className="w-full inline-flex items-center justify-center px-8 py-4 rounded-xl text-base font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-md transition-all mb-4"
                >
                  Choose Category & Book — ₹199
                </Link>

                <span className="text-xs text-slate-400">
                  100% Refund Guarantee if interviewer fails to contact within SLA.
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS */}
      <section id="how-it-works" className="py-20 sm:py-28 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest mb-3">
              Simple Journey
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              How Your Mock Interview Works
            </h3>
            <p className="text-slate-600">
              No complicated calendars or expired temporary slot holds. Seamless, human-coordinated scheduling.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 text-center">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                1
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Choose Category</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Select from System Design, DSA, AI, Full Stack, Frontend, or Backend.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                2
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Upload Resume & JD</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Upload your resume (PDF/DOCX) and paste your target job description.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                3
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Pay ₹199 Securely</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Pay 19,900 paise securely via Razorpay UPI, Netbanking, or Cards.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                4
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Same-Day Email</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Interviewer personally emails you today to coordinate your interview time.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80">
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto mb-4">
                5
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Attend Interview</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Join the 45–60 minute session via Google Meet/Zoom and receive expert feedback.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. FAQS */}
      <section id="faqs" className="py-20 sm:py-28 bg-slate-50 border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest mb-3">
              Clear Answers
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Frequently Asked Questions
            </h3>
            <p className="text-slate-600">
              Everything you need to know about our scheduling, interview format, and policies.
            </p>
          </div>

          <div className="space-y-4">
            {FAQS.map((faq, i) => (
              <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="flex items-start gap-3">
                  <HelpCircle className="w-5 h-5 text-sky-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-slate-900 text-base mb-2">
                      {faq.question}
                    </h4>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 6. FINAL CALL TO ACTION */}
      <section className="py-16 sm:py-24 bg-slate-900 text-white text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">
            Ready to Ace Your Technical Interviews?
          </h3>
          <p className="text-slate-400 text-base sm:text-lg mb-8 max-w-xl mx-auto">
            Book your 45–60 minute mock interview today for ₹199. Practice real engineering scenarios with an experienced interviewer.
          </p>
          <Link
            href="#categories"
            className="inline-flex items-center justify-center px-8 py-4 rounded-xl text-base font-bold text-slate-900 bg-white hover:bg-slate-100 shadow-xl transition-all"
          >
            Get Started — ₹199
          </Link>
        </div>
      </section>

      <Footer />
    </>
  );
}
