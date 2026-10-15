import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Premium Human-Led Mock Interviews | Prepare Smarter. Perform Better.",
  description: "One-on-one live technical mock interviews conducted by experienced human software engineers. System Design, DSA, AI Engineer, Full Stack, Frontend, Backend.",
  keywords: ["mock interview", "system design interview", "dsa interview", "technical interview prep india", "human led mock interview"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col antialiased bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
