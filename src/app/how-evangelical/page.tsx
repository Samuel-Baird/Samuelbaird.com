import type { Metadata } from "next";
import { EvangelicalQuizApp } from "@/components/evangelical-quiz/quiz-app";
import { SurveyFooter } from "@/components/evangelical-quiz/survey-footer";

// Unlisted: not in the nav, not in sitemap.ts, shared by direct link only.
export const metadata: Metadata = {
  title: "How evangelical are you?",
  description:
    "Answer belief statements from a national survey and see which religious tradition you answer most like.",
  robots: { index: false, follow: false },
};

export default function HowEvangelicalPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-2xl">
          <EvangelicalQuizApp />
        </div>
        {/* Sourcing marginalia, per the honesty requirement that it appear on
            every screen — one persistent aside rather than a footer repeated
            inside each quiz step. Stacks below the quiz on mobile. */}
        <aside className="mt-10 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <SurveyFooter />
        </aside>
      </div>
    </div>
  );
}
