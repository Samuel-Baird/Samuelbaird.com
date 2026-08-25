"use client";

import { useEffect, useState } from "react";
import { printSelfTest, QUIZ_DATA, runSelfTest, type AnswerMap } from "@/lib/evangelical-quiz";
import { LandingScreen } from "./landing-screen";
import { QuestionScreen } from "./question-screen";
import { ResultsScreen } from "./results-screen";

type Step = "landing" | "question" | "results";

/**
 * Client-side quiz state machine: landing -> one screen per question,
 * answerable in either direction -> results. Nothing here talks to a
 * server — scoring runs entirely against the bundled data.json, per the
 * build order (route + UI + client-side scoring first, database later).
 */
export function EvangelicalQuizApp() {
  const [step, setStep] = useState<Step>("landing");
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<AnswerMap>({});

  const items = QUIZ_DATA.items;
  const current = items[index];

  // Exposed for the console test block the build spec asks for: run
  // `runEvangelicalQuizSelfTest()` in devtools on this page.
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") {
      (window as unknown as Record<string, unknown>).runEvangelicalQuizSelfTest = () =>
        printSelfTest(runSelfTest(QUIZ_DATA));
    }
  }, []);

  function start() {
    setIndex(0);
    setStep("question");
  }

  function answer(responseIndex: number) {
    setAnswers((a) => ({ ...a, [current.id]: responseIndex }));
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
  }

  if (step === "landing" || !current) {
    return <LandingScreen onStart={start} />;
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

  return <ResultsScreen answers={answers} onRetake={retake} />;
}
