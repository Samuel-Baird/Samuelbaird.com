"use client";

import { useEffect, useState } from "react";

/**
 * Renders text that briefly appears in the Deseret alphabet before
 * "translating" itself into Latin, character by character.
 *
 * The effect is decorative. The server render and the first client render are
 * plain Latin text, so crawlers, no-JS visitors, and anyone with reduced
 * motion enabled only ever get the real title; the Deseret pass is added
 * after mount and removed when it finishes.
 *
 * Deseret is a phonemic alphabet, so there is no true letter-for-letter
 * transliteration of English. The map below picks a plausible glyph per
 * Latin letter for the sake of the animation — it is not a real
 * transliteration and nothing meaningful is ever encoded in it.
 */

const DESERET_LOWER: Record<string, string> = {
  a: "\u{10430}",
  b: "\u{1043A}",
  c: "\u{1043F}",
  d: "\u{1043C}",
  e: "\u{1042F}",
  f: "\u{10441}",
  g: "\u{10440}",
  h: "\u{10438}",
  i: "\u{1042E}",
  j: "\u{1043E}",
  k: "\u{1043F}",
  l: "\u{1044A}",
  m: "\u{1044B}",
  n: "\u{1044C}",
  o: "\u{1042C}",
  p: "\u{10439}",
  q: "\u{1043F}",
  r: "\u{10449}",
  s: "\u{10445}",
  t: "\u{1043B}",
  u: "\u{10433}",
  v: "\u{10442}",
  w: "\u{10436}",
  x: "\u{10446}",
  y: "\u{10437}",
  z: "\u{10446}",
};

/** Deseret capitals sit 0x28 below their lowercase counterparts. */
const CASE_OFFSET = 0x28;

function toDeseret(char: string): string {
  const lower = DESERET_LOWER[char.toLowerCase()];
  if (!lower) return char;
  if (char === char.toLowerCase()) return lower;
  return String.fromCodePoint(lower.codePointAt(0)! - CASE_OFFSET);
}

const DURATION_MS = 300;
const MAX_STAGGER_MS = 50;
const TOTAL_STAGGER_BUDGET_MS = 850;
const FONT_TIMEOUT_MS = 300;

type Props = {
  text: string;
  className?: string;
  /**
   * "always" replays on every mount (page titles, where the reveal is the
   * page's one moment of ceremony). "session" plays once per browser session
   * (the nav wordmark, which remounts on every navigation).
   */
  replay?: "always" | "session";
  sessionKey?: string;
};

export function DeseretTitle({
  text,
  className,
  replay = "always",
  sessionKey,
}: Props) {
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const storageKey = `deseret:${sessionKey ?? text}`;
    if (replay === "session") {
      try {
        if (window.sessionStorage.getItem(storageKey)) return;
      } catch {
        // Private mode or blocked storage: fall through and just animate.
      }
    }

    let cancelled = false;

    // Animating before the Deseret face is ready would flash tofu boxes.
    const ready = document.fonts
      ? Promise.race([
          document.fonts.load('1rem "Noto Sans Deseret"'),
          new Promise((resolve) => setTimeout(resolve, FONT_TIMEOUT_MS)),
        ]).then(() => document.fonts.check('1rem "Noto Sans Deseret"'))
      : Promise.resolve(false);

    const stagger = Math.min(
      MAX_STAGGER_MS,
      TOTAL_STAGGER_BUDGET_MS / Math.max(text.length, 1),
    );
    let done: ReturnType<typeof setTimeout>;

    ready.then((available) => {
      if (cancelled || !available) return;
      setAnimating(true);
      try {
        window.sessionStorage.setItem(storageKey, "1");
      } catch {
        // Non-fatal: the animation just replays next navigation.
      }
      done = setTimeout(
        () => {
          if (!cancelled) setAnimating(false);
        },
        stagger * text.length + DURATION_MS + 60,
      );
    });

    return () => {
      cancelled = true;
      clearTimeout(done);
    };
  }, [replay, sessionKey, text]);

  if (!animating) {
    return <span className={className}>{text}</span>;
  }

  const stagger = Math.min(
    MAX_STAGGER_MS,
    TOTAL_STAGGER_BUDGET_MS / Math.max(text.length, 1),
  );

  // Split into words and the whitespace between them, keeping both. The word
  // is the smallest unit that goes in the layout: splitting Latin per
  // character would let the line break mid-word ("creat" / "or") and would
  // drop kerning, so the title reflowed the moment the animation collapsed
  // back to a plain text node. Words stay whole text nodes, and only the
  // Deseret overlay — which is absolutely positioned and therefore weightless
  // — is split per character for the stagger.
  const parts = text.split(/(\s+)/).filter((part) => part !== "");
  // Character offset each part starts at, so a part's glyphs keep their place
  // in the single stagger running across the whole title.
  const starts: number[] = [];
  for (let i = 0, seen = 0; i < parts.length; i += 1) {
    starts.push(seen);
    seen += parts[i].length;
  }

  return (
    <span className={className} aria-label={text}>
      {parts.map((part, partIndex) => {
        const start = starts[partIndex];

        if (/^\s+$/.test(part)) {
          // A real space between inline-blocks, so lines still break here.
          return (
            <span key={partIndex} aria-hidden="true" className="whitespace-pre">
              {part}
            </span>
          );
        }

        const chars = Array.from(part);
        // The Latin word resolves once its last glyph has finished turning
        // over, so the title reads as translating word by word.
        const wordDelay = `${Math.round((start + chars.length - 1) * stagger)}ms`;

        return (
          <span
            key={partIndex}
            aria-hidden="true"
            className="relative inline-block"
          >
            <span
              style={{
                animation: `deseret-in ${DURATION_MS}ms ease-out ${wordDelay} both`,
              }}
            >
              {part}
            </span>
            <span
              className="pointer-events-none absolute inset-0 flex items-center justify-center"
              style={{ fontFamily: "var(--font-deseret), sans-serif" }}
            >
              {chars.map((char, charIndex) => (
                <span
                  key={charIndex}
                  style={{
                    animation: `deseret-out ${DURATION_MS}ms ease-in ${Math.round(
                      (start + charIndex) * stagger,
                    )}ms both`,
                  }}
                >
                  {toDeseret(char)}
                </span>
              ))}
            </span>
          </span>
        );
      })}
    </span>
  );
}
