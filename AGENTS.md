<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Shipping your work

Finish the job: commit, push, and merge without waiting to be asked. Work that
sits unmerged on a branch pending approval is not done, and the repo owner
would rather review something that already landed than be asked for permission
at every step. Only stop short of merging when explicitly told to.

Two things that are still worth doing carefully:

- **Commit your own files, by path.** This checkout is sometimes shared with
  another concurrent session. `git add -A` will sweep up that session's
  half-finished work and push it under your commit message. Run `git status`
  first, and stage the files you actually changed.
- **Merge working code.** Get the build green and check your change on the
  Vercel preview before merging. Shipping fast is the default; shipping broken
  is not.

# Design

Read [BRANDING_AND_DESIGN.md](BRANDING_AND_DESIGN.md) before writing or changing
any UI. It is the design source of truth, not a suggestion — new pages and
components must follow it so the site stays coherent.

The things most often gotten wrong:

- **Every public page fills the `mx-auto max-w-6xl px-5 sm:px-8` rail.** Do not
  build a page on a narrow centered column — it leaves dead whitespace down both
  sides. Keep prose at a readable measure inside the rail and use the remaining
  width for an aside, a sticky table of contents, or related content.
- One radius site-wide: `rounded-[var(--radius)]`. No `rounded-full` pills, no
  `rounded-2xl` cards.
- Borders, not shadows. Colors from CSS tokens only — never a raw hex or a default
  Tailwind ramp like `emerald-100`.
- All badges use the shared `<Tag>` component with one of its five ink families.
- Gate any new animation on `prefers-reduced-motion`.
- **Maps:** read [docs/MAPS.md](docs/MAPS.md). Every world map uses the shared
  `ChoroplethMap` (banded colors, round legend cut-offs, zoom, Save PNG). Do not
  build a one-off map.
