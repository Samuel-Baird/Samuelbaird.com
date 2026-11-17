-- Remove the versions feature (changelog_documents, changelog_versions, changelog_sections)
drop table if exists changelog_sections cascade;
drop table if exists changelog_versions cascade;
drop table if exists changelog_documents cascade;
