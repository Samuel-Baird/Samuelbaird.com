# How to access team documents (Teams chats and channels) with Claude

Worked out 2026-11-16 for the ME 4810 capstone team. Teams "files" are ordinary SharePoint/OneDrive files, so the Microsoft 365 connector can search and read them. Read-only. Keep the copies private (team work, outside contacts); `courses/capstone/` is gitignored for that reason.

## What the connector can do (UVU account)
Granted scopes include Files.Read.All, Sites.Read.All, Chat.Read, ChannelMessage.Read.All, Channel.ReadBasic.All, Mail.Read, Calendars.Read. Missing: `Team.ReadBasic.All`, so "list my teams" fails with FORBIDDEN (only a UVU admin can grant it). Everything below still works without it.

| Need | Tool | Notes |
|---|---|---|
| Find files by name/content | `sharepoint_search` (query, fileType, afterDateTime) | Finds team-site files and files in teammates' OneDrives that were shared with you |
| Find folders | `sharepoint_folder_search` | |
| List a folder | `read_resource` with `file:///{driveId}/{folderItemId}` | Use the `uri` the search returns; `file:///{driveId}/` lists the drive root |
| Read a file as text | `read_resource` on a file uri | docx, pptx, xlsx, pdf, txt/csv/json. Use `startPage`/`endPage` for long docs; workbooks return one sheet per page and show formulas |
| List my group chats | `teams_list_chats` (page with `nextCursor`) | Gives chat ids, topics and members |
| Find messages / attachments | `chat_message_search` (query `*`, `hasAttachment: true`, `afterDateTime`) | Returns message uris and chat ids; filter by chat id yourself |
| Read one message | `read_resource` on the `teams:///chats/{chatId}/messages/{id}` uri | The body has the link to the shared file and the OneDrive path |
| Channel messages | `teams_list_channel_messages` | Needs the team id; get it from the `channelUri` in `chat_message_search` results (percent-decode it) |

## Where Teams files live
- **Channel files** live in the team's SharePoint site, library "Shared Documents", in a folder per channel. A **private channel** gets its own site (for example `ME-4810-0012026Fall-FullTerm-Drone`), so "the drone channel" is that site, not a folder in the class site.
- **Files shared in a chat** live in the sender's OneDrive (usually `Documents` or `Microsoft Teams Chat Files`) and are only readable if they were shared with you. Chat message attachments carry `contentUrl`; search for the file by name with `sharepoint_search` to get its `file:///` uri (the web link alone cannot be read: https URLs are not supported by `read_resource`).
- Class notebooks (OneNote, `.one`) and Loop files show up in search, but contents are only partly readable.

## Workflow used
1. `teams_list_chats` to get the chat ids; `chat_message_search` with `hasAttachment` to see what was shared and when.
2. `sharepoint_folder_search` / `sharepoint_search` to find the team site (search on the course/team name), then `read_resource` on its root and subfolders.
3. `read_resource` each file and save the text locally as markdown (for this project: `courses/capstone/`, with an `INDEX.md` listing local path, original link and who shared it).

## Limits to expect
- **Text only.** Images, zips, photos, slide graphics and scanned content are not returned; no binary download exists in the connector. For originals, open the web link in a browser and download from there.
- Inline images in chat messages have no readable file.
- `.url` shortcut files are not readable (open the `webUrl`).
- Drafts change: copies are snapshots; note the date.
- Search results are capped (25-50 per page, use `nextOffset`/`offset`); attachment searches return channel posts from every team you are in, so filter by chat id.
- Read-only: it cannot edit files in SharePoint or Teams. Sending messages from Teams needs separate, explicit approval.

## Example
The full set pulled for the ME 4810 drone team (SharePoint site files, memos, meeting notes, and documents shared in the two team chats) is indexed in `courses/capstone/INDEX.md` (local only).
