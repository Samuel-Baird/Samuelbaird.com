"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  claimEvangelicalQuizRuns,
  clearEvangelicalQuizAnswers,
  recordEvangelicalQuizRun,
  saveEvangelicalDemographics,
  saveEvangelicalQuizAnswer,
} from "@/app/actions/evangelical-quiz";
import { printSelfTest, QUIZ_DATA, runSelfTest, type AnswerMap } from "@/lib/evangelical-quiz";
import {
  EMPTY_DEMOGRAPHICS,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";
import {
  clearAnonId,
  getOrCreateAnonId,
  markDemographicsAsked,
  peekAnonId,
  readStoredDemographics,
  storeDemographics,
  wasDemographicsAsked,
} from "./anon-store";
import { DemographicsScreen } from "./demographics-screen";
import { LandingScreen } from "./landing-screen";
import { QuestionScreen } from "./question-screen";
import { ResultsScreen } from "./results-screen";

type Step = "landing" | "demographics" | "question" | "results";

/**
 * Client-side quiz state machine: landing -> optional one-time demographic
 * intake -> one screen per question, answerable in either direction ->
 * results. Scoring runs entirely against the bundled data.json - a
 * signed-out reader can take the whole quiz with zero network. Signed-in
 * answers persist per-question (evangelical_quiz_answers); every completed
 * run - anonymous included - is recorded once as an append-only snapshot
 * (evangelical_quiz_runs) for aggregate analysis, with the score
 * recomputed server-side.
 */
export function EvangelicalQuizApp({
  initialAnswers,
  signedIn,
  needsDemographics,
}: {
  initialAnswers: AnswerMap;
  signedIn: boolean;
  /**
   * Server-side "should we ask" verdict: for signed-in readers, whether
   * profiles.demographics_updated_at is unset. Always true for anonymous
   * readers - the client refines that with its localStorage asked-flag.
   */
  needsDemographics: boolean;
}) {
  const [step, setStep] = useState<Step>("landing");
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<AnswerMap>(initialAnswers);
  const recordedRun = useRef(false);
  const pathname = usePathname() || "/how-evangelical";

  const items = QUIZ_DATA.items;
  const current = items[index];
  const answeredCount = Object.keys(answers).length;
  const hasFinished = answeredCount === items.length;

  // Exposed for the console test block the build spec asks for: run
  // `runEvangelicalQuizSelfTest()` in devtools on this page.
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") {
      (window as unknown as Record<string, unknown>).runEvangelicalQuizSelfTest = () =>
        printSelfTest(runSelfTest(QUIZ_DATA));
    }
  }, []);

  // Claim earlier anonymous runs into the account, once, after sign-in.
  useEffect(() => {
    if (!signedIn) return;
    const anonId = peekAnonId();
    if (!anonId) return;
    claimEvangelicalQuizRuns({ anonId })
      .then(() => clearAnonId())
      .catch((err) => console.error("Failed to claim anonymous quiz runs:", err));
  }, [signedIn]);

  function shouldAskDemographics(): boolean {
    if (!needsDemographics) return false;
    if (!signedIn && wasDemographicsAsked()) return false;
    return true;
  }

  function firstUnansweredIndex(): number {
    const i = items.findIndex((item) => answers[item.id] === undefined);
    return i === -1 ? 0 : i;
  }

  function start() {
    setIndex(0);
    setStep(shouldAskDemographics() ? "demographics" : "question");
  }

  function resume() {
    setIndex(firstUnansweredIndex());
    setStep(shouldAskDemographics() ? "demographics" : "question");
  }

  function viewResults() {
    setStep("results");
  }

  function finishDemographics(d: Demographics) {
    if (signedIn) {
      saveEvangelicalDemographics({ ...d, currentPath: pathname }).catch((err) => {
        console.error("Failed to save demographics:", err);
      });
    } else {
      storeDemographics(d);
      markDemographicsAsked();
    }
    setStep("question");
  }

  function skipDemographics() {
    finishDemographics(EMPTY_DEMOGRAPHICS);
  }

  function answer(responseIndex: number) {
    setAnswers((a) => ({ ...a, [current.id]: responseIndex }));
    if (signedIn) {
      saveEvangelicalQuizAnswer({
        itemId: current.id,
        responseIndex,
        currentPath: pathname,
      }).catch((err) => {
        // Local state stays authoritative either way - the quiz keeps
        // working even if persistence fails, it just won't be there next visit.
        console.error("Failed to save evangelical quiz answer:", err);
      });
    }
  }

  function recordRun(finalAnswers: AnswerMap) {
    if (recordedRun.current) return;
    recordedRun.current = true;
    const payload = signedIn
      ? { runId: crypto.randomUUID(), answers: finalAnswers }
      : {
          runId: crypto.randomUUID(),
          answers: finalAnswers,
          anonId: getOrCreateAnonId() ?? undefined,
          demographics: readStoredDemographics(),
        };
    // An anonymous browser with no storage at all has no anon id; that run
    // simply isn't recorded, and the reader still gets their results.
    if (!signedIn && !payload.anonId) return;
    recordEvangelicalQuizRun(payload).catch((err) => {
      console.error("Failed to record quiz run:", err);
    });
  }

  function continueToNext() {
    if (index + 1 < items.length) {
      setIndex(index + 1);
    } else {
      recordRun(answers);
      setStep("results");
    }
  }

  function back() {
    if (index === 0) {
      setStep("landing");
    } else {
      setIndex(index - 1);
    }
  }

  function retake() {
    setAnswers({});
    setIndex(0);
    setStep("landing");
    recordedRun.current = false;
    if (signedIn) {
      clearEvangelicalQuizAnswers({ currentPath: pathname }).catch((err) => {
        console.error("Failed to clear evangelical quiz answers:", err);
      });
    }
  }

  if (step === "landing" || !current) {
    return (
      <LandingScreen
        answeredCount={answeredCount}
        hasFinished={hasFinished}
        signedIn={signedIn}
        onStart={start}
        onResume={resume}
        onViewResults={viewResults}
      />
    );
  }

  if (step === "demographics") {
    return (
      <DemographicsScreen
        onSubmit={finishDemographics}
        onSkip={skipDemographics}
        onBack={() => setStep("landing")}
      />
    );
  }

  if (step === "question") {
    return (
      <QuestionScreen
        item={current}
        index={index}
        total={items.length}
        chosen={answers[current.id]}
        onAnswer={answer}
        onBack={back}
        onExit={() => setStep("landing")}
        onContinue={continueToNext}
        isLast={index + 1 >= items.length}
      />
    );
  }

  return <ResultsScreen answers={answers} onRetake={retake} signedIn={signedIn} />;
}
