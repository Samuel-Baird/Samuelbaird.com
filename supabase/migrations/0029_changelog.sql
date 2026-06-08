-- LDS Changelog — document version tracking
-- Documents → versions → sections (markdown-first). Public read, admin write.
-- Comparison/diff/AI-notes build on top of these tables in later phases.

-- ============================================================================
-- changelog_documents
-- ============================================================================
create table if not exists public.changelog_documents (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  summary text,
  category text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================================
-- changelog_versions  (one edition of a document)
-- ============================================================================
create table if not exists public.changelog_versions (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.changelog_documents(id) on delete cascade,
  label text not null,                       -- e.g. "2023 edition"
  published_on date,
  ordinal integer not null default 0,        -- display/sort order (oldest → newest)
  source_type text not null default 'markdown',
  source_url text,
  extraction_method text,                    -- e.g. 'manual', 'pdf-ocr' (later phase)
  confidence text,                           -- 'official-digital' | 'official-pdf' | 'archived' | 'printed-scan' | 'ocr-derived' | 'user-uploaded' | 'unverified'
  created_at timestamptz not null default now()
);

create index if not exists changelog_versions_document_idx
  on public.changelog_versions (document_id, ordinal);

-- ============================================================================
-- changelog_sections  (the unit later phases align and diff)
-- ============================================================================
create table if not exists public.changelog_sections (
  id uuid primary key default gen_random_uuid(),
  version_id uuid not null references public.changelog_versions(id) on delete cascade,
  ordinal integer not null default 0,
  heading text,
  body_markdown text,
  created_at timestamptz not null default now()
);

create index if not exists changelog_sections_version_idx
  on public.changelog_sections (version_id, ordinal);

-- ============================================================================
-- updated_at trigger (reuses public.set_updated_at from 0001)
-- ============================================================================
drop trigger if exists changelog_documents_set_updated_at on public.changelog_documents;
create trigger changelog_documents_set_updated_at
  before update on public.changelog_documents
  for each row execute function public.set_updated_at();

-- ============================================================================
-- Row Level Security: public read, admin write
-- (Server actions use the service role and bypass RLS; these policies are the
--  default-deny backstop so anon/non-admin sessions cannot write.)
-- ============================================================================
alter table public.changelog_documents enable row level security;
alter table public.changelog_versions enable row level security;
alter table public.changelog_sections enable row level security;

-- changelog_documents
drop policy if exists "changelog_documents: public read" on public.changelog_documents;
create policy "changelog_documents: public read" on public.changelog_documents
  for select using (true);

drop policy if exists "changelog_documents: admins insert" on public.changelog_documents;
create policy "changelog_documents: admins insert" on public.changelog_documents
  for insert with check (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_documents: admins update" on public.changelog_documents;
create policy "changelog_documents: admins update" on public.changelog_documents
  for update using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_documents: admins delete" on public.changelog_documents;
create policy "changelog_documents: admins delete" on public.changelog_documents
  for delete using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

-- changelog_versions
drop policy if exists "changelog_versions: public read" on public.changelog_versions;
create policy "changelog_versions: public read" on public.changelog_versions
  for select using (true);

drop policy if exists "changelog_versions: admins insert" on public.changelog_versions;
create policy "changelog_versions: admins insert" on public.changelog_versions
  for insert with check (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_versions: admins update" on public.changelog_versions;
create policy "changelog_versions: admins update" on public.changelog_versions
  for update using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_versions: admins delete" on public.changelog_versions;
create policy "changelog_versions: admins delete" on public.changelog_versions
  for delete using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

-- changelog_sections
drop policy if exists "changelog_sections: public read" on public.changelog_sections;
create policy "changelog_sections: public read" on public.changelog_sections
  for select using (true);

drop policy if exists "changelog_sections: admins insert" on public.changelog_sections;
create policy "changelog_sections: admins insert" on public.changelog_sections
  for insert with check (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_sections: admins update" on public.changelog_sections;
create policy "changelog_sections: admins update" on public.changelog_sections
  for update using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "changelog_sections: admins delete" on public.changelog_sections;
create policy "changelog_sections: admins delete" on public.changelog_sections
  for delete using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );
