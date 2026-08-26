import type { Metadata } from "next";
import { DownloadDataButton } from "@/components/evangelical-quiz/download-data-button";
import { EvangelicalQuizApp } from "@/components/evangelical-quiz/quiz-app";
import { SurveyFooter } from "@/components/evangelical-quiz/survey-footer";
import { getCurrentUser } from "@/lib/auth";
import { DATASETS } from "@/lib/data-explorer";
import { getEvangelicalQuizAnswersForUser } from "@/lib/evangelical-quiz/answers";
import { getPremiumStatus } from "@/lib/permissions";

// Unlisted: not in the nav, not in sitemap.ts, shared by direct link only.
export const metadata: Metadata = {
  title: "How evangelical are you?",
  description:
    "Answer belief statements from a national survey and see which religious tradition you answer most like.",
  robots: { index: false, follow: false },
};

// Reads the signed-in reader's premium status and saved answers.
export const dynamic = "force-dynamic";

const HOME_DATASET = DATASETS.find((d) => d.quiz?.href === "/how-evangelical");

export default async function HowEvangelicalPage() {
  const [{ premium }, auth] = await Promise.all([getPremiumStatus(), getCurrentUser()]);
  const initialAnswers = auth ? await getEvangelicalQuizAnswersForUser(auth.user.id) : {};

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-2xl">
          <EvangelicalQuizApp
            initialAnswers={initialAnswers}
            signedIn={Boolean(auth)}
            datasetHref={HOME_DATASET ? `/data-explorer/${HOME_DATASET.slug}` : null}
            needsDemographics={auth ? auth.profile?.demographics_updated_at == null : true}
          />
        </div>
        {/* Sourcing marginalia, per the honesty requirement that it appear on
            every screen — one persistent aside rather than a footer repeated
            inside each quiz step. Stacks below the quiz on mobile. */}
        <aside className="mt-10 space-y-6 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <SurveyFooter />
          <DownloadDataButton premium={premium} />
        </aside>
      </div>
    </div>
  );
}
