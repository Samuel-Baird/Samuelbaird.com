import type { Metadata } from "next";
import { PlannedTimelinePage } from "@/components/quiz/planned-timeline-page";

export const metadata: Metadata = {
  title: "Baptism — Source Timeline",
  description:
    "A planned source timeline on whether baptism effects the new birth or witnesses to one already worked, who may receive it, and whose baptism counts.",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

export default function BaptismTimelinePage() {
  return (
    <PlannedTimelinePage
      timeline="/baptism-timeline"
      title="baptism"
      deseretTitle="What the water does."
      question="Does baptism work the remission of sins and the new birth, or witness to a change already worked — and what has been claimed for it, by whom, and when?"
      lede="A chronological gathering of sources on what baptism is understood to accomplish: the old argument between regeneration and symbol, run through Latter-day Saint teaching and against the traditions it was arguing with."
      axes={[
        {
          title: "Efficacy",
          body: "Whether the ordinance effects what it signifies — remission, rebirth, cleansing — or testifies to a change already worked inwardly. The distinction the whole timeline turns on.",
        },
        {
          title: "Necessity",
          body: "Whether baptism is required for salvation without exception, ordinarily required with provision made for those who never had the opportunity, or not a condition at all.",
        },
        {
          title: "Agent and authority",
          body: "Who may perform it and what makes a baptism valid — authority held, words used, or form followed — and how rejected baptisms have been described.",
        },
        {
          title: "Infant baptism",
          body: "The age-of-accountability position and the arguments made against infant baptism, including the ones that predate the Restoration.",
        },
        {
          title: "Rebaptism",
          body: "The nineteenth-century practice of rebaptism for renewal, health, and gathering, its scale, and how and when it was retired.",
        },
      ]}
      sourcing="The Book of Mormon and Doctrine and Covenants, general conference addresses and the Conference Report, the Journal of Discourses for the Utah period, handbooks and missionary materials. Comparative statements from other traditions where a source is explicitly arguing against one."
    />
  );
}
