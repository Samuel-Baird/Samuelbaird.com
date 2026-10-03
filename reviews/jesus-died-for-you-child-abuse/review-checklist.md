# Gate A checklist — jesus-died-for-you-child-abuse

All 15 pre-Gate-A checks completed for the revised Saint Capybara script.

1. Adversarial review: both questions answered for all three claims in claims.md; independent opponent recheck passes.
2. Tone: manual sensitive-topic and affected-person passes; no polemics, ridicule, analogies, or allegation about the speaker's professional conduct.
3. Sources: strict source lint passes, zero errors or warnings. All six used source IDs inspected; exact card quotation verified.
4. Evidence grades: theology, interpretation, disputed empirical claims, and proposed teaching recommendations distinguished in claims.md and narration.
5. Doctrine versus opinion: canonical scripture tier 1; 2023 Primary curriculum dated and classified separately. No lower-tier assertion promoted to doctrine.
6. Clip fairness: continuous 0–8.95, 36.20–48.60, 48.75–58.38 spans; original hedges preserved. Each under 20 seconds. Source 30.98 seconds / 137.3 seconds = 22.56%, below 30%. Source credit retained. Transcript checked; no fresh audio certification.
7. Duration: 137.3-second estimate, within 60–180 seconds; narration timing remains an estimate pending approved TTS.
8. Sensitive: true; no amused/happy poses; no music.
9. Escalation: no unresolved ESCALATION.md; no claim relies on unverified research leads.
10. Brand: automated and manual review passes. Runtime identity tokens and example blacklist checked; the checkout's private custom blacklist is an empty placeholder, not a populated personal list.
11. Sprites: all resolved poses exist in the finalized sprite map; current source pose used for the quotation card. Final storyboard inspected.
12. Pronunciations: narration names covered by pronunciation entries or ok-as-is entries. Existing user-approved Moroni/Mosiah guidance retained; listen-through belongs after approval.
13. Clip poses: concerned, thoughtful, solemn match the source concerns.
14. Alignment: replies address preceding clips. n07 expressly identifies the debt question as elsewhere in the reel. Full timestamped transcript appended.
15. Critique: opponent, factcheck, editor completed; two major and four minor findings corrected and rechecked. No open findings.

## Workflow notes
beats.yaml is the source of truth; script.md is the generated, editable review copy. The current local template's Chatterbox host voice and speed 1.25 are preserved. Older branch documentation describing Kokoro does not override that existing project configuration.

The storyboard tool now selects clip-review text using word timestamps, preventing unplayed neighboring speech from appearing in a clip's review transcript. Two focused regression tests pass.

The intake workbook has a script-link column but no Video Generated column. The E46-only script-link update was prepared and verified with all other cells and workbook entries preserved, but saving is blocked because another process has the original workbook open. Queue update remains pending; the current wip note and other fields remain untouched. No status column is invented.

This package supersedes the earlier presenter-style script and its critique. Gate A is script review only; narration, clip cutting, and video rendering await user approval. Post-approval audio, caption, phone-legibility, metadata, and finished-video checks remain pending by design.
