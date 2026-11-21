-- 2026-11-21: add AI agent opt-in and custom instructions columns to public.admin_tickets
-- (owner request via Relay item #133).
-- Default false: existing tickets stay on hold until Samuel checks them.

alter table public.admin_tickets
  add column if not exists ai_enabled boolean not null default false,
  add column if not exists ai_instructions text not null default '';
