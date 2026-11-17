export const CONTACT_EMAIL = "ithinksamofficial@gmail.com";

export const mailto = (subject?: string) =>
  subject
    ? `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
    : `mailto:${CONTACT_EMAIL}`;
