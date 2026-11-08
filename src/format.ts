/** Helpers for shaping tool output. */
import { JspError } from "./jsp/client";

export const DEFAULT_MAX_CHARS = 20_000;

/** Return a window of `text`, with a note telling the model how to read on. */
export function windowText(text: string, offset = 0, maxChars = DEFAULT_MAX_CHARS): string {
  if (offset >= text.length && text.length > 0) {
    return `_(offset ${offset} is past the end; total length is ${text.length} characters.)_`;
  }
  if (offset === 0 && text.length <= maxChars) return text;
  let end = Math.min(text.length, offset + maxChars);
  if (end < text.length) {
    const nl = text.lastIndexOf("\n", end);
    if (nl > offset + maxChars * 0.6) end = nl;
  }
  const head = offset > 0 ? `_(continuing from character ${offset} of ${text.length})_\n\n` : "";
  const tail =
    end < text.length
      ? `\n\n_(truncated at character ${end} of ${text.length}; call again with offset=${end} to continue.)_`
      : "";
  return head + text.slice(offset, end) + tail;
}

export type ToolResult = {
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
};

export function ok(text: string): ToolResult {
  return { content: [{ type: "text", text }] };
}

export function fail(err: unknown): ToolResult {
  const msg =
    err instanceof JspError
      ? err.message
      : err instanceof Error
        ? `Error contacting the Joseph Smith Papers: ${err.message}`
        : String(err);
  return { content: [{ type: "text", text: msg }], isError: true };
}

export async function run(fn: () => Promise<string>, offset?: number, maxChars?: number): Promise<ToolResult> {
  try {
    return ok(windowText(await fn(), offset ?? 0, maxChars ?? DEFAULT_MAX_CHARS));
  } catch (err) {
    return fail(err);
  }
}
