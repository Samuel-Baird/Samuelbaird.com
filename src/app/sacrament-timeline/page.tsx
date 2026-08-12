import type { Metadata } from "next";
import { PlannedTimelinePage } from "@/components/quiz/planned-timeline-page";

export const metadata: Metadata = {
  title: "The sacrament — Source Timeline",
  description:
    "A planned source timeline on the emblems and the rite: symbolic memorial against forms of real presence, and high liturgy against plainness.",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

export default function SacramentTimelinePage() {
  return (
    <PlannedTimelinePage
      timeline="/sacrament-timeline"
      title="the sacrament"
      deseretTitle="Bread, water, and what they are."
      question="What have the emblems been said to be, what is partaking said to do, and how plainly or ceremonially has the rite been kept?"
      lede="A chronological gathering of sources on the sacrament: what the bread and the water are held to be, from memorial through the various accounts of a real presence, and how the form of the rite itself has moved — including the changes that are documented but rarely noticed."
      axes={[
        {
          title: "The emblems",
          body: "Whether the elements are held to be signs of remembrance, a means by which Christ is really if spiritually received, or bearers of a presence in some stronger sense.",
        },
        {
          title: "What partaking does",
          body: "Whether grace is conveyed by the ordinance, covenants already made are renewed, or the rite works on memory and will — and which of these the sacrament prayers themselves state.",
        },
        {
          title: "Liturgical register",
          body: "How fixed the rite is: set words and who may vary them, posture, vestment and its absence, and the deliberate plainness that has been claimed as a virtue.",
        },
        {
          title: "Worthiness and the table",
          body: "Who may administer and who may partake, how self-examination has been taught, and how restrictions have been framed and applied.",
        },
        {
          title: "Practice as it changed",
          body: "Documented changes in the elements, vessels, frequency, and prayers — wine to water, common cup to individual, and when each shift happened.",
        },
      ]}
      sourcing="The sacrament prayers as canonized, general conference addresses and the Conference Report, the Journal of Discourses, handbooks and instructions to bishoprics. Liturgical positions from other traditions where a source names one to agree or disagree with it."
    />
  );
}
