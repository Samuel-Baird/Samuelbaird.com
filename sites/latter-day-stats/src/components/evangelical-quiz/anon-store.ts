"use client";

import {
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";

/**
 * localStorage state for anonymous quiz-takers: a random UUID that ties
 * their completed runs together (and lets a later sign-in claim them),
 * their optional demographics until a completed run snapshots them, and
 * an "already asked" flag so the intake never re-nags. Everything is
 * try/catch-guarded - private browsing without storage just degrades to
 * a session-only experience, never an error.
 */

const KEY_ANON_ID = "eq_anon_id";
const KEY_DEMOGRAPHICS = "eq_demographics";
const KEY_ASKED = "eq_demographics_asked";

export function getOrCreateAnonId(): string | null {
  try {
    const existing = localStorage.getItem(KEY_ANON_ID);
    if (existing) return existing;
    const id = crypto.randomUUID();
    localStorage.setItem(KEY_ANON_ID, id);
    return id;
  } catch {
    return null;
  }
}

export function peekAnonId(): string | null {
  try {
    return localStorage.getItem(KEY_ANON_ID);
  } catch {
    return null;
  }
}

/** After a successful claim - the runs now belong to the account. */
export function clearAnonId(): void {
  try {
    localStorage.removeItem(KEY_ANON_ID);
  } catch {
    // nothing to do
  }
}

export function readStoredDemographics(): Demographics {
  try {
    const raw = localStorage.getItem(KEY_DEMOGRAPHICS);
    return validateDemographics(raw ? JSON.parse(raw) : null);
  } catch {
    return validateDemographics(null);
  }
}

export function storeDemographics(d: Demographics): void {
  try {
    localStorage.setItem(KEY_DEMOGRAPHICS, JSON.stringify(d));
  } catch {
    // session-only fallback
  }
}

export function wasDemographicsAsked(): boolean {
  try {
    return localStorage.getItem(KEY_ASKED) === "1";
  } catch {
    return false;
  }
}

export function markDemographicsAsked(): void {
  try {
    localStorage.setItem(KEY_ASKED, "1");
  } catch {
    // session-only fallback
  }
}
