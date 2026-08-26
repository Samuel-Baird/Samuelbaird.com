"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { clearEvangelicalQuizAnswers, saveEvangelicalQuizAnswer } from "@/app/actions/evangelical-quiz";
import { printSelfTest, QUIZ_DATA, runSelfTest, type AnswerMap } from "@/lib/evangelical-quiz";
import { LandingScreen } from "./landing-screen";
import { QuestionScreen } from "./question-screen";
import { ResultsScreen } from "./results-screen";

type Step = "landing" | "question" | "results";

/**
 * Client-side quiz state machine: landing -> one screen per question,
 * answerable in either direction -> results. Scoring runs entirely against
 * the bundled data.json - a signed-out reader never touches the network.
 * A signed-in reader's answers are additionally persisted one at a time
 * (evangelical_quiz_answers) so "Start" becomes "Continue" or "View
 * results" on their next visit; this never gates taking the quiz itself.
 */
export function EvangelicalQuizApp({
  initialAnswers,
  signedIn,
  datasetHref,
}: {
  initialAnswers: AnswerMap;
  signedIn: boolean;
  /** Where "back to the dataset" on the results screen should go. */
  datasetHref: string | null;
}) {
  const [step, setStep] = useState<Step>("landing");
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<AnswerMap>(initialAnswers);
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

  function firstUnansweredIndex(): number {
    const i = items.findIndex((item) => answers[item.id] === undefined);
    return i === -1 ? 0 : i;
  }

  function start() {
    setIndex(0);
    setStep("question");
  }

  function resume() {
    setIndex(firstUnansweredIndex());
    setStep("question");
  }

  function viewResults() {
    setStep("results");
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

  function continueToNext() {
    if (index + 1 < items.length) {
      setIndex(index + 1);
    } else {
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
        onStart={start}
        onResume={resume}
        onViewResults={viewResults}
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
        onContinue={continueToNext}
        isLast={index + 1 >= items.length}
      />
    );
  }

  return <ResultsScreen answers={answers} onRetake={retake} datasetHref={datasetHref} />;
}
