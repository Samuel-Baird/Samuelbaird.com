import { z } from "zod";

// Shared input schemas for server actions. These guard the service-role and
// RLS write paths against malformed ids/enums; UX-level checks (required
// fields, friendly messages) stay in the actions themselves.

export const targetTypeSchema = z.enum(["channel", "study"]);

export const toggleTargetSchema = z.object({
  targetType: targetTypeSchema,
  targetId: z.uuid(),
});

export const uuidSchema = z.uuid();

export const emailSchema = z.email().max(200);

// Free-text URL fields: admins sometimes paste without a protocol, so accept
// anything that looks like a link rather than strict z.url().
export const linkSchema = z
  .string()
  .trim()
  .max(500)
  .refine((v) => v === "" || /^https?:\/\//.test(v) || v.includes("."), {
    message: "Enter a valid link.",
  });

export const yearSchema = z.coerce
  .number()
  .int()
  .min(1500)
  .max(2200);

export function firstZodMessage(error: z.ZodError): string {
  return error.issues[0]?.message ?? "Invalid input.";
}

export const graphicPostSchema = z.object({
  datasetSlug: z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/),
  graphicId: z.string().max(120).regex(/^[a-z0-9][a-z0-9_-]*$/),
  posted: z.boolean(),
  postedDates: z.string().trim().max(500),
});
