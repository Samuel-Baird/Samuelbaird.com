import { getCurrentUser } from "@/lib/auth";
import { getQuizAnswersForUser } from "@/lib/quiz/answers";
import { QUIZ_SECTIONS, quizSectionFor } from "@/lib/quiz";
import { QuizRunner } from "./quiz-runner";

/**
 * Server half of the quiz: resolves who is signed in and what they have
 * already answered, then hands both to the client runner. Used by each
 * timeline page for its own questions and by /quiz for the whole bank.
 */
export async function Quiz({
  timeline,
  signInReason,
}: {
  /** A timeline href for that timeline's questions, or omitted for all of them. */
  timeline?: string;
  signInReason: string;
}) {
  const auth = await getCurrentUser();
  const answers = auth ? await getQuizAnswersForUser(auth.user.id) : {};

  const sections = timeline
    ? [quizSectionFor(timeline)].filter((s) => s !== null)
    : QUIZ_SECTIONS;

  if (sections.length === 0) return null;

  return (
    <QuizRunner
      sections={sections}
      initialAnswers={answers}
      signedIn={Boolean(auth)}
      signInReason={signInReason}
    />
  );
}
