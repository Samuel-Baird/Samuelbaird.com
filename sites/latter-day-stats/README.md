# Latter-day Stats

An independent research site covering the Latter-day Saint community: creator
statistics, curated academic studies, and a data explorer of survey and
compiled datasets on Latter-day Saint demographics, belief, and culture.

No institutional affiliation with The Church of Jesus Christ of Latter-day
Saints, BYU, or any tracked creator.

---

## Stack

| | |
|---|---|
| Framework | Next.js 16 (App Router) · React 19 |
| Language | TypeScript, `strict`, path alias `@/*` → `src/*` |
| Styling | Tailwind CSS v4 — no config file; design tokens are CSS variables in `src/app/globals.css` |
| Data | Supabase (Postgres + auth + storage) |
| Hosting | Cloudflare Workers (OpenNext), worker `latter-day-stats` |
| Package manager | npm |

> **This is not the Next.js you may know.** Version 16 has breaking changes
> against older training data and tutorials. Read the bundled guides in
> `node_modules/next/dist/docs/` before writing framework code — see
> [`AGENTS.md`](./AGENTS.md).

---

## Getting started

```bash
npm ci
cp .env.local.example .env.local   # then fill in real values
npm run dev                        # http://localhost:3000
```

`.env.local` holds the Supabase URL and keys, the YouTube Data API key used by
the stats refresh, and the admin/cron secrets. It is gitignored — never commit
real keys.

Most pages need a reachable Supabase project.

### Scripts

| Command | Does |
|---|---|
| `npm run dev` | Development server |
| `npm run build` | Production build — also runs the strict typecheck |
| `npm run start` | Serve a production build |
| `npm run lint` | ESLint 9 (flat config, `eslint-config-next`) |

There is **no test framework**. Verification is `npm run lint`, `npm run build`,
and exercising the affected pages in a browser.

---

## Layout

```
src/app/            routes (App Router); route folders may colocate their own
                    components, data, and schema — colocated files are not routable
src/components/     shared components, flat, kebab-case filenames
src/lib/            data access, auth, types; src/lib/supabase/ holds the clients
supabase/migrations/  numbered SQL migrations
scripts/            one-off maintenance and seeding scripts (tsx / node),
                    plus the statistics-graphics generators:
                    scripts/social-graphics/ (R, Instagram posts) and
                    scripts/state-of-theology-graphics/ (Python, website) -
                    each has its own README/style guide
content/            static source texts (e.g. King Follett scribal accounts)
docs/               project documentation
```

### Database migrations

Migrations are plain SQL, applied in **alphabetical filename order** by
`scripts/migrate.ts`, which records each applied filename in a
`schema_migrations` table.

```bash
npx tsx scripts/migrate.ts
```

> **Never reuse a migration number or filename.** The runner skips any filename
> already recorded, so a second file with an existing name is silently never
> applied. Always take the next free number.

---

## Documentation

| Document | Covers |
|---|---|
| [`AGENTS.md`](./AGENTS.md) | Rules for AI agents working in this repo |
| [`BRANDING_AND_DESIGN.md`](./BRANDING_AND_DESIGN.md) | Design source of truth — type scale, colour tokens, card and pill styles, voice |
| [`STUDY_UPLOAD_INSTRUCTIONS.md`](./STUDY_UPLOAD_INSTRUCTIONS.md) | Adding an academic study |

---

## Design conventions

Read [`BRANDING_AND_DESIGN.md`](./BRANDING_AND_DESIGN.md) before writing UI. The
two rules most easily got wrong:

- **Tailwind v4 needs complete literal class strings.** Never build a class name
  by concatenation. Map variants to full strings in a `Record` — see
  `src/lib/channel-types.ts`.
- **Card surfaces use `bg-white`.** `globals.css` remaps `.bg-white` under
  to the dark surface, so do not add `dark:bg-*` variants for cards.
  Consume colours as `text-[color:var(--muted)]`,
  `border-[color:var(--border)]`, and so on.

The site is dark only: the root layout puts `class="dark"` on `<html>` and there
is no theme toggle. A drifting-glyph background (`public/bg/glyph-field.js`)
sits behind every page. Serif type is the global `.serif` utility (Fraunces), not
`font-serif`.

---

## Contributing

Commit messages and pull requests should explain **why**, not just what. When a
change fixes a bug, say what the bug actually was.

Before pushing: `npm run lint` and `npm run build` both clean, and the affected
pages checked at mobile and desktop widths.
