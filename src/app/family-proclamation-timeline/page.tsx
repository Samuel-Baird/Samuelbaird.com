import type { Metadata } from "next";
import { PlannedTimelinePage } from "@/components/quiz/planned-timeline-page";

export const metadata: Metadata = {
  title: "The Family: A Proclamation to the World — Source Timeline",
  description:
    "A planned source timeline on eternal gender, the family forms exaltation is said to require, and the status of the 1995 Proclamation.",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

export default function FamilyProclamationTimelinePage() {
  return (
    <PlannedTimelinePage
      timeline="/family-proclamation-timeline"
      title="the family"
      deseretTitle="The family, proclaimed."
      question="What has been taught about gender as an eternal characteristic, about the family forms exaltation requires, and about what kind of document the 1995 Proclamation is?"
      lede="A chronological gathering of the sources behind “The Family: A Proclamation to the World” — the teachings it drew on, the drafting and the status claimed for it since, and how each of its claims had been stated before 1995 and since."
      axes={[
        {
          title: "Heavenly Parents",
          body: "Statements that we are the offspring of heavenly parents, and what work the plural is doing in each. This axis overlaps the eternal-increase timeline, and shared sources will be linked across rather than duplicated.",
        },
        {
          title: "Eternal gender",
          body: "Whether gender is stated to be an essential characteristic of premortal, mortal, and eternal identity — and, where it is, whether what that amounts to is ever spelled out.",
        },
        {
          title: "Family form and exaltation",
          body: "What form of family is said to be required for exaltation, and whether exceptions or unexplained cases are acknowledged alongside the pattern.",
        },
        {
          title: "Roles by divine design",
          body: "Statements assigning responsibilities within the family by design rather than by circumstance, and the qualifications attached to them over time.",
        },
        {
          title: "Drafting history and status",
          body: "How the document was produced and presented, and how its authority has been characterised since — revelation, inspired counsel, or a statement of position — including by those who signed it.",
        },
      ]}
      sourcing="General conference addresses and the Conference Report, First Presidency statements, the 1995 Proclamation itself and its presentation, Church handbooks and curriculum, and the Gospel Topics essays. Reception and drafting history from scholarly literature, graded as citations rather than counted as independent attestation."
    />
  );
}
